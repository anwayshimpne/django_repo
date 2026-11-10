from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import Choice, Course, Lesson, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course.objects.prefetch_related("lessons__questions__choices"), pk=course_id)
    return render(request, "onlinecourse/course_details_bootstrap.html", {"course": course})


@login_required
def submit(request, lesson_id):
    lesson = get_object_or_404(Lesson.objects.prefetch_related("questions__choices"), pk=lesson_id)
    if request.method != "POST":
        return redirect("onlinecourse:course_details", course_id=lesson.course_id)

    questions = list(lesson.questions.all())
    question_ids = {question.pk for question in questions}
    selected_ids = set()
    correct_count = 0
    for question in questions:
        value = request.POST.get(f"question_{question.pk}")
        if not value:
            continue
        choice = Choice.objects.filter(pk=value, question_id=question.pk).first()
        if choice:
            selected_ids.add(choice.pk)
            if choice.is_correct:
                correct_count += 1

    score = round(correct_count * 100 / len(questions)) if questions else 0
    with transaction.atomic():
        submission = Submission.objects.create(learner=request.user, lesson=lesson, score=score)
        submission.selected_choices.set(Choice.objects.filter(pk__in=selected_ids, question__lesson_id=lesson.pk))
    return redirect("onlinecourse:show_exam_result", submission_id=submission.pk)


@login_required
def show_exam_result(request, submission_id):
    submission = get_object_or_404(
        Submission.objects.select_related("lesson__course", "learner").prefetch_related(
            "lesson__questions__choices", "selected_choices"
        ),
        pk=submission_id,
        learner=request.user,
    )
    selected_ids = set(submission.selected_choices.values_list("pk", flat=True))
    results = []
    for question in submission.lesson.questions.all():
        choices = list(question.choices.all())
        results.append({
            "question": question,
            "choices": choices,
            "selected_ids": selected_ids,
            "correct": any(choice.pk in selected_ids and choice.is_correct for choice in choices),
        })
    return render(request, "onlinecourse/exam_result.html", {"submission": submission, "results": results})
