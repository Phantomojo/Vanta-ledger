import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import "swiper/swiper-bundle.css";
import "simplebar-react/dist/simplebar.min.css";
import App from "./App.tsx";
import { AppWrapper } from "./components/common/PageMeta.tsx";
import { ThemeProvider } from "./context/ThemeContext.tsx";
import Documents from "./pages/Documents";
import Ledger from "./pages/Ledger";
import Companies from "./pages/Companies";
import Projects from "./pages/Projects";
import Subcontractors from "./pages/Subcontractors";
import Users from "./pages/Users";
import Analytics from "./pages/Analytics";
import AiNlpPage from "./pages/AiNlp";
import Settings from "./pages/Settings";
import Notifications from "./pages/Notifications";
import Paperless from "./pages/Paperless";
import ReviewTools from "./pages/ReviewTools";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ThemeProvider>
      <AppWrapper>
        <App />
      </AppWrapper>
    </ThemeProvider>
  </StrictMode>
);
