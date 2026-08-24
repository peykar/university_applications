import React from "react";
import ReactDOM from "react-dom/client";
import "./styles.css";

type University = {
  id: string;
  slug_en: string;
  name_en: string;
  city: string;
  logo?: string | null;
};

function App() {
  const [universities, setUniversities] = React.useState<University[]>([]);
  const [error, setError] = React.useState("");

  React.useEffect(() => {
    fetch("/api/v1/universities/")
      .then((response) => {
        if (!response.ok) throw new Error("Failed to load universities");
        return response.json();
      })
      .then(setUniversities)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <main>
      <h1>TurkDemy</h1>
      <p>React/Vite frontend consuming the Django REST API.</p>
      {error && <p>{error}</p>}
      <ul>
        {universities.map((university) => (
          <li key={university.id}>
            <strong>{university.name_en}</strong>
            {university.city ? ` — ${university.city}` : ""}
          </li>
        ))}
      </ul>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
