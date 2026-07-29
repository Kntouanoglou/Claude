import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getCourse } from "../api.js";

export default function CourseDetailPage() {
  const { courseId } = useParams();
  const [course, setCourse] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    setCourse(null);
    setError(null);
    getCourse(courseId)
      .then(setCourse)
      .catch((err) => setError(err.message || "Failed to load course."));
  }, [courseId]);

  if (error) return <p className="error">{error}</p>;
  if (!course) return <p className="muted">Loading...</p>;

  return (
    <section>
      <h1>{course.title}</h1>
      <p>{course.description}</p>

      {course.modules.length === 0 && <p className="muted">No modules yet.</p>}

      {course.modules.map((module) => (
        <div className="module" key={module.id}>
          <h2>{module.title}</h2>
          <p className="muted">{module.description}</p>

          {module.concepts.map((concept) => (
            <div className="concept" key={concept.id}>
              <h3>{concept.title}</h3>
              <p style={{ whiteSpace: "pre-wrap" }}>{concept.content}</p>
              <p className="concept-meta">
                from: {concept.source_material_title} &middot; imported{" "}
                {new Date(concept.created_at).toLocaleString()}
              </p>
            </div>
          ))}
        </div>
      ))}
    </section>
  );
}
