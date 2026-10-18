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

  const moduleCount = course.modules.length;
  const conceptCount = course.modules.reduce((sum, m) => sum + m.concepts.length, 0);

  return (
    <section>
      <header className="course-header">
        <h1>{course.title}</h1>
        <p>{course.description}</p>
        <p className="concept-meta">
          {moduleCount} module{moduleCount === 1 ? "" : "s"} &middot; {conceptCount} concept
          {conceptCount === 1 ? "" : "s"}
        </p>
      </header>

      {moduleCount === 0 && <p className="muted">No modules yet.</p>}

      {moduleCount > 0 && (
        <div className="course-layout">
          <nav className="course-toc">
            <p className="toc-label">Contents</p>
            <ol>
              {course.modules.map((module, mIndex) => (
                <li key={module.id}>
                  <a href={`#module-${module.id}`}>{module.title}</a>
                  {module.concepts.length > 0 && (
                    <ol className="toc-concepts">
                      {module.concepts.map((concept, cIndex) => (
                        <li key={concept.id}>
                          <a href={`#concept-${concept.id}`}>
                            {mIndex + 1}.{cIndex + 1} {concept.title}
                          </a>
                        </li>
                      ))}
                    </ol>
                  )}
                </li>
              ))}
            </ol>
          </nav>

          <div className="course-content">
            {course.modules.map((module, mIndex) => (
              <div className="module-card" id={`module-${module.id}`} key={module.id}>
                <div className="module-heading">
                  <span className="badge badge-module">Module {mIndex + 1}</span>
                  <h2>{module.title}</h2>
                </div>
                <p className="muted">{module.description}</p>

                {module.concepts.length === 0 && (
                  <p className="muted">No concepts yet.</p>
                )}

                {module.concepts.map((concept, cIndex) => (
                  <div className="concept-card" id={`concept-${concept.id}`} key={concept.id}>
                    <div className="concept-heading">
                      <span className="badge badge-concept">
                        {mIndex + 1}.{cIndex + 1}
                      </span>
                      <h3>{concept.title}</h3>
                    </div>
                    <p className="concept-summary">{concept.summary}</p>
                    {concept.key_points?.length > 0 && (
                      <ul className="concept-key-points">
                        {concept.key_points.map((point, i) => (
                          <li key={i}>{point}</li>
                        ))}
                      </ul>
                    )}
                    <p className="concept-body" style={{ whiteSpace: "pre-wrap" }}>
                      {concept.content}
                    </p>
                    <p className="concept-meta">
                      from: {concept.source_material_title} &middot; imported{" "}
                      {new Date(concept.created_at).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
