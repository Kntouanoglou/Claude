import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listCourses } from "../api.js";

export default function CourseListPage() {
  const [courses, setCourses] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    listCourses()
      .then(setCourses)
      .catch((err) => setError(err.message || "Failed to load courses."));
  }, []);

  return (
    <section>
      <h1>Courses</h1>

      {error && <p className="error">{error}</p>}
      {!error && courses === null && <p className="muted">Loading...</p>}
      {courses && courses.length === 0 && (
        <p className="muted">
          No courses yet — go <Link to="/import">import something</Link>.
        </p>
      )}

      {courses &&
        courses.map((course) => (
          <div className="card" key={course.id}>
            <h3>
              <Link to={`/courses/${course.id}`}>{course.title}</Link>
            </h3>
            <p>{course.description}</p>
            <p className="concept-meta">
              {course.module_count} module{course.module_count === 1 ? "" : "s"} &middot;{" "}
              {course.concept_count} concept{course.concept_count === 1 ? "" : "s"}
            </p>
          </div>
        ))}
    </section>
  );
}
