# This Python file uses the following encoding: utf-8

import re, random, datetime, math
import os.path
import logging
from itertools import chain

from django import forms
from django.db.models import F, Q

from django.core.files.uploadedfile import UploadedFile
from django_localflavor_us import forms as usforms, us_states
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model, authenticate
from datetime import datetime

from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

from problem_roulette.models import (UserSession, Course, UserQuestion,
    ExamTemplate, ExamTopicQuestions, QuestionAnswer, QuestionUserFeedback,
    ParticipantGroupMember, ParticipantGroup)

class CourseMixin(object):
    _course = None

    def get_course(self):
        return self._course

    def set_course(self, course):
        self._course = self._course = course

class UserMixin(object):
    _user = None

    def get_user(self):
        return self._user

    def set_user(self, user):
        self._user = user

class CourseForm(CourseMixin, forms.ModelForm):

    def __init__(self, course, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.set_course(course=course)

class UserForm(UserMixin, forms.ModelForm):

    def __init__(self, user, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.set_user(user=user)

class CourseUserForm(UserMixin, CourseMixin, forms.ModelForm):

    def __init__(self, course, user, *args, **kwargs):
        super(CourseUserForm, self).__init__(*args, **kwargs)
        self.set_course(course=course)
        self.set_user(user)

class UserSessionForm(CourseUserForm):
    validation_errors = {'invalid_topics': forms.ValidationError}
    total_questions = forms.IntegerField(required=False,
        widget=forms.NumberInput(attrs={
            'class': 'num-question-field form-control'}))

    def __init__(self, topic_list=None, user_group_member=None, *args, **kwargs):
        super(UserSessionForm, self).__init__(*args, **kwargs)
        self.user_group_member = user_group_member
        self.fields['topics'].queryset = self.get_course().selection_topics
        self.fields['total_questions'].help_text = """There are a total of %s questions in this course
                                                   """ % self.get_course().active_questions.count()
        if topic_list:
            self.initial['topics'] = topic_list

    class Meta:
        model = UserSession
        fields = ['timed', 'total_questions','topics']
        widgets = {'topics': forms.CheckboxSelectMultiple(attrs={'class': 'topic-option-select'})}
        labels = {'timed': 'Keep a timer for this session?'}

    def clean_topics(self):
        topics = self.cleaned_data.get('topics',[])
        return topics

    def clean_timed(self):
        timed = self.cleaned_data.get('timed', [])
        return timed

    def save(self, commit=True):
        instance = super(UserSessionForm, self).save(commit=False)
        instance.user = self.get_user()
        instance.course = self.get_course()
        instance.subject = instance.course.subject
        instance.group_id = self.user_group_member.group_id if self.user_group_member else None

        if not instance.start_time:
            instance.start_time = datetime.now()
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class UserQuestionForm(UserForm):
    user_question = None
    question = None
    ANSWER_WIDGETS = {'radio': forms.RadioSelect,
                      'checkbox': forms.CheckboxSelectMultiple,
                      'text': forms.TextInput}

    answers = forms.MultipleChoiceField(required=True)

    def __init__(self, user_question, *args, **kwargs):
        super(UserQuestionForm, self).__init__(*args, **kwargs)
        self.user_question = user_question
        self.question = user_question.question

        self.fields['answers'].widget = self.answer_widget()

        self.fields['answers'].choices = [(q.id, mark_safe(q.text)) for q in self.user_question.repeatable_answers_list]

    class Meta:
        model = UserQuestion
        fields = []

    @property
    def answer_widget(self):
        return self.ANSWER_WIDGETS[self.question.question_type]

    @property
    def answer_options(self):
        return self.question.answers

    def save(self, commit=True):
        if commit:
            self.user_question.create_answers(self.cleaned_data.get('answers'))
            self.user_question.is_correct()

        return self.user_question

class QuestionUserFeedbackForm(UserForm):

    class Meta:
        model = QuestionUserFeedback
        fields = ['clarity', 'believed_incorrect', 'copyright', 'explanation']
        widgets = {'clarity': forms.RadioSelect(choices=QuestionUserFeedback.CLARITY_OPTIONS)}

class ExamTemplateForm(CourseUserForm):

    class Meta:
        model = ExamTemplate
        fields = ['name','duration']

class ExamTopicQuestionsForm(CourseForm):
    MAX_TOPIC_QUESTIONS = 100

    class Meta:
        model = ExamTopicQuestions
        exclude = ['template']

    def __init__(self, *args, **kwargs):
        super(ExamTopicQuestionsForm, self).__init__(*args, **kwargs)
        self.fields['topic'].queryset = self.get_course().topics
        self.fields['topic_questions'].label = 'Number of questions'

    def clean_topic_questions(self):
        topic_questions = self.cleaned_data.get('topic_questions')
        if int(topic_questions) > self.MAX_TOPIC_QUESTIONS:
            raise forms.ValidationError('You must select fewer than {} questions per topic.'.format(self.MAX_TOPIC_QUESTIONS))
        return topic_questions
