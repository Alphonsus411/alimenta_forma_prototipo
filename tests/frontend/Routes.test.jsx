import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import App from '../../src/App';
import ErrorBoundary from '../../src/components/ErrorBoundary';
import ProfileFooter from '../../src/components/ProfileFooter';

const renderRoute = (route) => render(
  <MemoryRouter initialEntries={[route]}>
    <App />
  </MemoryRouter>,
);

describe('rutas principales', () => {
	it('ofrece en el perfil únicamente enlaces con destino real y nombre accesible', () => {
		render(
			<MemoryRouter>
				<ProfileFooter />
			</MemoryRouter>,
		);

		const navigation = screen.getByRole('navigation', { name: 'Navegación del perfil' });
		const links = screen.getAllByRole('link');

		expect(navigation).toContainElement(links[0]);
		expect(links).toHaveLength(4);
		expect(links.map((link) => [link.textContent, link.getAttribute('href')])).toEqual([
			['Inicio', '/'],
			['Identificarse', '/login'],
			['Mi progreso', '/student'],
			['Mi perfil', '/profile'],
		]);
		links.forEach((link) => expect(link).toHaveAccessibleName());
	});

  it.each([
    ['/courses', 'Nuestros Cursos'],
    ['/membership', 'Nuestros Precios'],
    ['/about', 'Acerca de'],
    ['/faqs', 'Preguntas Frecuentes'],
    ['/login', 'Inicio de Sesión'],
    ['/register', 'Registro de usuario'],
		['/coorp', 'Formación para empresas'],
		['/jobs', 'Oportunidades profesionales'],
		['/teacher', 'Panel docente'],
  ])('renderiza %s con su encabezado accesible', (route, heading) => {
    renderRoute(route);

    expect(screen.getByRole('heading', { name: heading })).toBeInTheDocument();
  });

	it.each([
		['/coorp', 'Solicitar propuesta comercial', 'mailto:empresas@alimentaforma.es'],
		['/jobs', 'Contactar con empleo', 'mailto:empleo@alimentaforma.es'],
	])('ofrece una acción accesible en %s', (route, linkName, destination) => {
		renderRoute(route);

		expect(screen.getByRole('main')).toBeInTheDocument();
		expect(screen.getByRole('link', { name: linkName })).toHaveAttribute('href', expect.stringContaining(destination));
	});

	it('navega desde la cabecera a la propuesta para empresas', async () => {
		const user = userEvent.setup();
		renderRoute('/about');

		await user.click(screen.getByRole('link', { name: 'Empresas' }));

		expect(screen.getByRole('heading', { name: 'Formación para empresas', level: 1 })).toBeInTheDocument();
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

  it('muestra una página comprensible para una ruta desconocida y permite volver al inicio', async () => {
    const user = userEvent.setup();
    renderRoute('/ruta-que-no-existe');

    expect(screen.getByRole('heading', { name: 'Página no encontrada' })).toBeInTheDocument();
    expect(screen.getByText(/dirección que has solicitado no existe/i)).toBeInTheDocument();

    await user.click(screen.getByRole('link', { name: 'Volver al inicio' }));

    expect(screen.queryByRole('heading', { name: 'Página no encontrada' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Reintentar' })).toBeInTheDocument();
  });

  it('permite recuperar el contenido tras un fallo inesperado de renderizado', async () => {
    const user = userEvent.setup();
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    let shouldFail = true;
    const UnstableContent = () => {
      if (shouldFail) {
        throw new Error('Fallo de renderizado simulado');
      }
      return <p>Contenido recuperado</p>;
    };

    render(
      <ErrorBoundary onReset={() => { shouldFail = false; }}>
        <UnstableContent />
      </ErrorBoundary>,
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: 'Intentar de nuevo' }));
    expect(screen.getByText('Contenido recuperado')).toBeInTheDocument();
    consoleError.mockRestore();
  });
});
