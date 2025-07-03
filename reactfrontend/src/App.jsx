import './styles/layout.scss';

// main UI components
import Nav from './components/Nav/Nav'
import Aside from './components/Aside/Aside'
import Content from './components/Content/Content'


function App() {
  return (
    <div className="layout">
        <Nav/>
        <Aside/>
        <Content />
    </div>
  );
}

export default App;
