import { useState } from "react";
import "./App.css";
import PublicationCounter from "./components/PublicationCounter/PublicationCounter";
import packageJson from '../package.json';

const version = packageJson.version;

function App() {
  const [showModal, setShowModal] = useState(true);

  const closeModal = () => {
    setShowModal(false);
  };

  return (
    <div className="App">
      {/* Deprecation Banner */}
      <div className="deprecation-banner">
        ⚠️ Notice: This application will be deprecated on February 10th, 2026. Please migrate to the new version at Pubcounter.io ⚠️
      </div>

      {/* Deprecation Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>ℹ️ Important Notice</h3>
              <button className="modal-close" onClick={closeModal}>×</button>
            </div>
            <div className="modal-body">
              <p><strong>Thank you for using the Pubcounter Inventory Helper Version 0!</strong></p>
              <p>
                We have made major improvements based on your valuable feedback, and a new and much improved version is now available for beta testing!
              </p>
              <p>
                To learn more and get started with the new version, please contact <strong>Andrew Leon</strong> or visit{" "}
                <a href="https://pubcounter.io" target="_blank" rel="noopener noreferrer">Pubcounter.io</a>.
              </p>
              <div className="modal-warning">
                📅 <strong>Pubcounter V0's last day is February 10th, 2026.</strong><br />
                Please make plans to migrate and register for the new version before this date.
              </div>
            </div>
            <div className="modal-footer">
              <button className="modal-button" onClick={closeModal}>
                ✓ Got it, thanks!
              </button>
            </div>
          </div>
        </div>
      )}

      <header className="App-header">
        <h6>PubCounter v{version}</h6>
      </header>
      <PublicationCounter></PublicationCounter>
    </div>
  );
}

export default App;
