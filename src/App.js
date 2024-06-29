import "./App.css";
import PublicationCounter from "./components/PublicationCounter/PublicationCounter";
import PubCounterFlyoutNav from "./components/PubCounterFlyoutNav/PubCounterFlyoutNav";
import packageJson from "../package.json";

const version = packageJson.version;

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <PubCounterFlyoutNav></PubCounterFlyoutNav>
      </header>
      <PublicationCounter></PublicationCounter>
    </div>
  );
}

export default App;
