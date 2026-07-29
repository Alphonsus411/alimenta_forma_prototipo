import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import RegisterForm from '../../src/components/RegisterForm';
import { register } from '../../src/services/authApi';

vi.mock('../../src/services/authApi', () => ({ register: vi.fn() }));

const completeForm = async (user) => {
  await user.type(screen.getByLabelText(/nombre de usuario/i), 'alumna');
  await user.type(screen.getByLabelText(/correo/i), 'alumna@example.com');
  await user.type(screen.getByLabelText(/^nombre \*/i), 'Ana');
  await user.type(screen.getByLabelText(/apellido/i), 'López');
  await user.type(screen.getByLabelText(/^contraseña \*/i), 'ClaveSegura_2026');
  await user.type(screen.getByLabelText(/confirmación/i), 'ClaveSegura_2026');
};

describe('RegisterForm', () => {
  beforeEach(() => vi.clearAllMocks());

  it('registra sin recargar y muestra confirmación', async () => {
    register.mockResolvedValue({ username: 'alumna' });
    const user = userEvent.setup();
    render(<MemoryRouter><RegisterForm /></MemoryRouter>);
    await completeForm(user);
    await user.click(screen.getByRole('button', { name: /registrarse/i }));

    expect(register).toHaveBeenCalledWith(expect.objectContaining({
      username: 'alumna', email: 'alumna@example.com', category: 's',
    }));
    expect(await screen.findByRole('status')).toHaveTextContent('se creó correctamente');
  });

  it('presenta errores asociados a su campo', async () => {
    register.mockRejectedValue({ message: 'Error', fields: { email: ['Este correo ya existe.'] } });
    const user = userEvent.setup();
    render(<MemoryRouter><RegisterForm /></MemoryRouter>);
    await completeForm(user);
    await user.click(screen.getByRole('button', { name: /registrarse/i }));

    expect(await screen.findByText('Este correo ya existe.')).toBeInTheDocument();
  });
});
