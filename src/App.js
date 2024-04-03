import "./App.css";
import PublicationCounter from "./PublicationCounter";
import packageJson from '../package.json';

const version = packageJson.version;

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h6>PubCounter v{version}</h6>
      </header>
      <PublicationCounter></PublicationCounter>
    </div>
  );
}

export default App;
