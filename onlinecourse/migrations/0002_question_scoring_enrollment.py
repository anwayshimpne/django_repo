from django.db import migrations, models
import django.db.models.deletion


def migrate_existing_exam_data(apps, schema_editor):
    Enrollment = apps.get_model("onlinecourse", "Enrollment")
    Question = apps.get_model("onlinecourse", "Question")
    Submission = apps.get_model("onlinecourse", "Submission")
    db = schema_editor.connection.alias

    for question in Question.objects.using(db).select_related("lesson__course").all():
        question.course_id = question.lesson.course_id
        question.content = question.prompt[:200]
        question.save(using=db, update_fields=["course", "content"])

    for submission in Submission.objects.using(db).all():
        enrollment, _ = Enrollment.objects.using(db).get_or_create(
            learner_id=submission.learner_id,
            course_id=submission.course_id,
        )
        submission.enrollment_id = enrollment.pk
        submission.save(using=db, update_fields=["enrollment"])


def reverse_exam_data_migration(apps, schema_editor):
    # The old learner/course submission columns are restored by reverse schema operations.
    pass


class Migration(migrations.Migration):
    dependencies = [("onlinecourse", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="Enrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_enrolled", models.DateTimeField(auto_now_add=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="onlinecourse.course")),
                ("learner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="onlinecourse.learner")),
            ],
        ),
        migrations.AddField(
            model_name="question", name="content",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="question", name="grade",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="question", name="course",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="onlinecourse.course"),
        ),
        migrations.AddField(
            model_name="submission", name="enrollment",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="onlinecourse.enrollment"),
        ),
        migrations.RunPython(migrate_existing_exam_data, reverse_exam_data_migration),
        migrations.AlterField(
            model_name="question", name="course",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="onlinecourse.course"),
        ),
        migrations.AlterField(
            model_name="submission", name="enrollment",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="onlinecourse.enrollment"),
        ),
        migrations.RemoveField(model_name="submission", name="learner"),
        migrations.RemoveField(model_name="submission", name="course"),
        migrations.AddConstraint(
            model_name="enrollment",
            constraint=models.UniqueConstraint(fields=("learner", "course"), name="unique_learner_course_enrollment"),
        ),
    ]
