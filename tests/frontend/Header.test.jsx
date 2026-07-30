import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import Header from '../../src/components/Header';

const renderHeader = (route = '/') => render(
  <MemoryRouter initialEntries={[route]}>
    <Header />
  </MemoryRouter>,
);

describe('cabecera accesible', () => {
  it('relaciona el botón con el menú y comunica su nombre y estado', async () => {
    const user = userEvent.setup();
    renderHeader();

    const button = screen.getByRole('button', { name: 'Abrir menú' });
    const menu = screen.getByRole('list');

    expect(button).toHaveAttribute('type', 'button');
    expect(button).toHaveAttribute('aria-expanded', 'false');
    expect(button).toHaveAttribute('aria-controls', menu.id);

    await user.click(button);

    expect(screen.getByRole('button', { name: 'Cerrar menú' })).toHaveAttribute('aria-expanded', 'true');
  });

  it('permite abrir el menú y alcanzar sus enlaces solo con teclado', async () => {
    const user = userEvent.setup();
    renderHeader();

    await user.tab();
    const button = screen.getByRole('button', { name: 'Abrir menú' });
    expect(button).toHaveFocus();

    await user.keyboard('{Enter}');
    expect(button).toHaveAttribute('aria-expanded', 'true');

    await user.tab();
    expect(screen.getByRole('link', { name: 'Inicio' })).toHaveFocus();
  });

  it('señala el enlace correspondiente a la ruta activa', () => {
    renderHeader('/courses');

    expect(screen.getByRole('link', { name: 'Nuestros Cursos' })).toHaveAttribute('aria-current', 'page');
    expect(screen.getByRole('link', { name: 'Inicio' })).not.toHaveAttribute('aria-current');
  });
});
