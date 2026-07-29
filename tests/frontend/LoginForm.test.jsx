import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import LoginForm from '../../src/components/LoginForm';
import { login } from '../../src/services/authApi';

vi.mock('../../src/services/authApi', () => ({ login: vi.fn() }));

describe('LoginForm', () => {
  beforeEach(() => vi.clearAllMocks());

  it('envía campos controlados y muestra el resultado correcto', async () => {
    login.mockResolvedValue({ username: 'alumna' });
    const user = userEvent.setup();
    render(<MemoryRouter><LoginForm /></MemoryRouter>);

    await user.type(screen.getByLabelText(/nombre de usuario/i), 'alumna');
    await user.type(screen.getByLabelText(/contraseña/i), 'ClaveSegura_2026');
    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }));

    expect(login).toHaveBeenCalledWith({ username: 'alumna', password: 'ClaveSegura_2026' });
    expect(await screen.findByRole('status')).toHaveTextContent('Sesión iniciada como alumna');
  });

  it('muestra el error devuelto por el servidor', async () => {
    login.mockRejectedValue({ message: 'Error', fields: { non_field_errors: ['Credenciales incorrectas.'] } });
    const user = userEvent.setup();
    render(<MemoryRouter><LoginForm /></MemoryRouter>);

    await user.click(screen.getByRole('button', { name: /iniciar sesión/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent('Credenciales incorrectas');
  });
});
