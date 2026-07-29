const BASE = "/api";

async function handle(response) {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // ignore — non-JSON error body
    }
    throw new Error(detail);
  }
  return response.json();
}

export async function importMaterial({ title, text, file }) {
  const form = new FormData();
  form.append("title", title);
  if (text) form.append("text", text);
  if (file) form.append("file", file);

  const response = await fetch(`${BASE}/import`, {
    method: "POST",
    body: form,
  });
  return handle(response);
}

export async function listCourses() {
  const response = await fetch(`${BASE}/courses`);
  return handle(response);
}

export async function getCourse(courseId) {
  const response = await fetch(`${BASE}/courses/${courseId}`);
  return handle(response);
}

export async function getSourceMaterial(sourceMaterialId) {
  const response = await fetch(`${BASE}/source-materials/${sourceMaterialId}`);
  return handle(response);
}
