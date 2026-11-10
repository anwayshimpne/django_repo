from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .models import Choice, Course, Enrollment, Learner, Question, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course.objects.prefetch_related("lessons__questions__choices"), pk=course_id)
    return render(request, "onlinecourse/course_details_bootstrap.html", {"course": course})


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course.objects.prefetch_related("lessons__questions__choices"), pk=course_id)
    if request.method != "POST":
        return redirect("onlinecourse:course_details", course_id=course.pk)

    learner = get_object_or_404(Learner, user=request.user)
    if not learner.enrolled_courses.filter(pk=course.pk).exists():
        return HttpResponseForbidden("You must be enrolled in this course to submit the exam.")

    enrollment, _ = Enrollment.objects.get_or_create(learner=learner, course=course)
    questions = list(Question.objects.filter(course=course).prefetch_related("choices"))
    selected_ids = set()
    for question in questions:
        value = request.POST.get(f"question_{question.pk}")
        if not value:
            continue
        choice = next((item for item in question.choices.all() if str(item.pk) == value), None)
        if choice:
            selected_ids.add(choice.pk)

    possible_points = sum(question.grade for question in questions)
    earned_points = sum(
        question.is_get_score(
            selected_ids.intersection(question.choices.values_list("id", flat=True))
        )
        for question in questions
    )
    grade = round(earned_points * 100 / possible_points) if possible_points else 0
    with transaction.atomic():
        submission = Submission.objects.create(enrollment=enrollment, score=grade)
        submission.selected_choices.set(Choice.objects.filter(
            pk__in=selected_ids, question__course=course
        ))
    return redirect("onlinecourse:show_exam_result", course_id=course.pk, submission_id=submission.pk)


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    learner = get_object_or_404(Learner, user=request.user)
    enrollment = get_object_or_404(Enrollment, learner=learner, course=course)
    submission = get_object_or_404(
        Submission.objects.prefetch_related("selected_choices"),
        pk=submission_id,
        enrollment=enrollment,
    )
    selected_ids = set(submission.selected_choices.values_list("pk", flat=True))
    questions = list(Question.objects.filter(course=course).prefetch_related("choices"))

    # Recalculate from the course question set and this submission's selected choices.
    possible_points = sum(question.grade for question in questions)
    earned_points = sum(
        question.is_get_score(
            selected_ids.intersection(question.choices.values_list("id", flat=True))
        )
        for question in questions
    )
    grade = round(earned_points * 100 / possible_points) if possible_points else 0
    results = [{"question": question, "choices": question.choices.all()} for question in questions]

    return render(request, "onlinecourse/exam_result_bootstrap.html", {
        "course": course,
        "submission": submission,
        "selected_ids": selected_ids,
        "grade": grade,
        "results": results,
    })
