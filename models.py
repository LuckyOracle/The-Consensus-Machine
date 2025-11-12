# In a Django app (e.g., 'core/models.py')

from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. The User Model
class User(AbstractUser):
    """
    Extends the default Django user to add a reputation score.
    """
    reputation = models.IntegerField(default=1, help_text="User's reputation score, influences quiz/vote power.")

# 2. The Core Topics
class Topic(models.Model):
    """
    A high-level subject that can be voted on (e.g., "Climate Change", "Global Health").
    """
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# 3. The Quiz Engine
class Quiz(models.Model):
    """
    A collection of questions related to a Topic. This is the "knowledge test".
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="quizzes")
    title = models.CharField(max_length=255)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # The community-vetted reputation of the quiz itself (for fairness, accuracy)
    reputation_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    """
    A single question within a Quiz.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    source_link = models.URLField(blank=True, null=True, help_text="Link to source for fact-checking.")

    def __str__(self):
        return self.text[:50] + "..."

class Choice(models.Model):
    """
    A multiple-choice answer for a Question.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False, help_text="Is this the correct answer?")

    def __str__(self):
        return self.text

class QuizAttempt(models.Model):
    """
    Records a User's attempt at a Quiz, "unlocking" their vote on a Topic.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.FloatField() # e.g., 85.0 (for 85%)
    passed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quiz') # User can only have one main attempt

# 4. The Voting System
class Proposal(models.Model):
    """
    The specific item being voted on within a Topic.
    e.g., Topic="Climate", Proposal="Ratify the Global Emissions Treaty"
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="proposals")
    title = models.CharField(max_length=500)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True) # Is the vote open?

    def __str__(self):
        return self.title

class Vote(models.Model):
    """
    A single, cast vote by a User on a specific Proposal.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name="votes")
    # Using an integer for simple Yes/No/Abstain or ranked choice
    # 1 = Yes, 0 = No, 2 = Abstain
    choice = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only vote once on each proposal
        unique_together = ('user', 'proposal')
