from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="Instructor", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="instructor_profile", to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name="Course", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=200)),
            ("description", models.TextField(blank=True)),
            ("instructors", models.ManyToManyField(blank=True, related_name="courses", to="onlinecourse.instructor")),
        ]),
        migrations.CreateModel(name="Learner", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="learner_profile", to=settings.AUTH_USER_MODEL)),
            ("enrolled_courses", models.ManyToManyField(blank=True, related_name="learners", to="onlinecourse.course")),
        ]),
        migrations.CreateModel(name="Lesson", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=200)),
            ("content", models.TextField(blank=True)),
            ("order", models.PositiveIntegerField(default=0)),
            ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lessons", to="onlinecourse.course")),
        ], options={"ordering": ["order", "id"]}),
        migrations.CreateModel(name="Question", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("prompt", models.TextField()),
            ("order", models.PositiveIntegerField(default=0)),
            ("lesson", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="onlinecourse.lesson")),
        ], options={"ordering": ["order", "id"]}),
        migrations.CreateModel(name="Choice", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("text", models.CharField(max_length=500)),
            ("is_correct", models.BooleanField(default=False)),
            ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="choices", to="onlinecourse.question")),
        ]),
        migrations.CreateModel(name="Submission", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("score", models.PositiveIntegerField(default=0)),
            ("submitted_at", models.DateTimeField(auto_now_add=True)),
            ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="onlinecourse.course")),
            ("learner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="onlinecourse.learner")),
            ("selected_choices", models.ManyToManyField(blank=True, related_name="submissions", to="onlinecourse.choice")),
        ], options={"ordering": ["-submitted_at"]}),
    ]
