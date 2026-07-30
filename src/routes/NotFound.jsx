import { Link } from 'react-router-dom';
import Header from '../components/Header';

const NotFound = () => (
  <>
    <Header />
    <main className="routeFeedback">
      <h1>Página no encontrada</h1>
      <p>La dirección que has solicitado no existe o ya no está disponible.</p>
      <Link to="/">Volver al inicio</Link>
    </main>
  </>
);

export default NotFound;
