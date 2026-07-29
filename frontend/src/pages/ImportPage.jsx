import { useState } from "react";
import { Link } from "react-router-dom";
import { importMaterial } from "../api.js";

const ACTION_LABELS = {
  new_course: "Created a new course",
  add_to_course: "Added to an existing course",
  new_concept_in_course: "Added as a new concept in an existing course",
};

export default function ImportPage() {
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    setResult(null);
    try {
      const outcome = await importMaterial({ title, text, file });
      setResult(outcome);
      setTitle("");
      setText("");
      setFile(null);
    } catch (err) {
      setError(err.message || "Import failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section>
      <h1>Import material</h1>
      <p className="muted">
        Give it a title and some text (paste, or upload a .txt file). The AI decides
        everything else — whether this starts a new course, extends an existing one, or
        adds a single concept to one.
      </p>

      <form onSubmit={handleSubmit}>
        <label htmlFor="title">Title</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Python List Comprehensions"
          required
        />

        <label htmlFor="text">Text</label>
        <textarea
          id="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste an article, transcript, or notes here..."
        />

        <label htmlFor="file">Or upload a .txt file (optional, used if text is empty)</label>
        <input
          id="file"
          type="file"
          accept=".txt,text/plain"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />

        <div>
          <button type="submit" disabled={submitting || !title}>
            {submitting ? "Thinking..." : "Import"}
          </button>
        </div>
      </form>

      {error && (
        <div className="card">
          <p className="error">{error}</p>
        </div>
      )}

      {result && (
        <div className="card">
          <span className="badge">{ACTION_LABELS[result.action] || result.action}</span>
          <p>{result.reasoning}</p>
          <p>
            <Link to={`/courses/${result.course_id}`}>View "{result.course_title}"</Link>
          </p>
        </div>
      )}
    </section>
  );
}
