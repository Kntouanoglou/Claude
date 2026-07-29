import { NavLink, Route, Routes, Navigate } from "react-router-dom";
import ImportPage from "./pages/ImportPage.jsx";
import CourseListPage from "./pages/CourseListPage.jsx";
import CourseDetailPage from "./pages/CourseDetailPage.jsx";

export default function App() {
  return (
    <>
      <nav>
        <strong>AI Course-Builder</strong>
        <NavLink to="/import">Import</NavLink>
        <NavLink to="/courses">Courses</NavLink>
      </nav>
      <Routes>
        <Route path="/" element={<Navigate to="/import" replace />} />
        <Route path="/import" element={<ImportPage />} />
        <Route path="/courses" element={<CourseListPage />} />
        <Route path="/courses/:courseId" element={<CourseDetailPage />} />
      </Routes>
    </>
  );
}
