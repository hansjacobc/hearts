import { useGameSocket } from './useGameSocket'

function App() {
  const status = useGameSocket("test-room", "test-player");
  return (
    <div>
      <h1>Hearts</h1>
      <p>Socket status: {status}</p>
    </div>
  );
}

export default App;