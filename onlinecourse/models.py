from django.conf import settings
from django.db import models


class Instructor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="instructor_profile")

    def __str__(self):
        return self.user.get_username()


class Learner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="learner_profile")
    enrolled_courses = models.ManyToManyField("Course", blank=True, related_name="learners")

    def __str__(self):
        return self.user.get_username()


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructors = models.ManyToManyField(Instructor, blank=True, related_name="courses")

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    date_enrolled = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("learner", "course"), name="unique_learner_course_enrollment")]

    def __str__(self):
        return f"{self.learner} — {self.course}"


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="questions")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="questions")
    content = models.CharField(max_length=200, blank=True)
    prompt = models.TextField(blank=True)
    grade = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.content or self.prompt[:80]

    def is_get_score(self, selected_ids):
        """Return this question's points only when the submitted answer set is exact."""
        correct_ids = set(self.choices.filter(is_correct=True).values_list("id", flat=True))
        return self.grade if correct_ids and set(selected_ids) == correct_ids else 0

    def get_score(self, selected_ids):
        return self.is_get_score(selected_ids)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="submissions")
    selected_choices = models.ManyToManyField(Choice, blank=True, related_name="submissions")
    score = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    @property
    def learner(self):
        return self.enrollment.learner

    @property
    def course(self):
        return self.enrollment.course

    def __str__(self):
        return f"{self.enrollment} ({self.score}%)"
