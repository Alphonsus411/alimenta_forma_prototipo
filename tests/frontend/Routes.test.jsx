import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import App from '../../src/App';

const renderRoute = (route) => render(
  <MemoryRouter initialEntries={[route]}>
    <App />
  </MemoryRouter>,
);

describe('rutas principales', () => {
  it.each([
    ['/courses', 'Nuestros Cursos'],
    ['/membership', 'Nuestros Precios'],
    ['/about', 'Acerca de'],
    ['/faqs', 'Preguntas Frecuentes'],
    ['/login', 'Inicio de Sesión'],
    ['/register', 'Registro de usuario'],
  ])('renderiza %s con su encabezado accesible', (route, heading) => {
    renderRoute(route);

    expect(screen.getByRole('heading', { name: heading })).toBeInTheDocument();
  });

  it('navega desde el inicio al catálogo mediante un enlace', async () => {
    const user = userEvent.setup();
    renderRoute('/');

    await user.click(screen.getByRole('link', { name: 'Nuestros Cursos' }));

    expect(screen.getByRole('heading', { name: 'Nuestros Cursos' })).toBeInTheDocument();
  });

  it('asocia etiquetas con todos los controles del formulario de acceso', () => {
    renderRoute('/login');

    expect(screen.getByLabelText('Nombre de usuario *')).toHaveAttribute('name', 'username');
    expect(screen.getByLabelText('Contraseña *')).toHaveAttribute('type', 'password');
    expect(screen.getByRole('button', { name: 'Iniciar sesión' })).toBeEnabled();
  });
});
