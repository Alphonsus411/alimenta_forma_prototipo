import { useState } from "react";
import { NavLink } from "react-router-dom";
import { FaBars, FaTimes } from "react-icons/fa";
import styles from "./HeaderStyles.module.css";

const MENU_ID = "navegacion-principal";

const navigationItems = [
	{ to: "/", label: "Inicio", end: true },
	{ to: "/courses", label: "Nuestros Cursos" },
	{ to: "/membership", label: "Nuestros Precios" },
	{ to: "/about", label: "Acerca de" },
	{ to: "/faqs", label: "Preguntas Frecuentes" },
	{ to: "/coorp", label: "Empresas" },
	{ to: "/jobs", label: "Empleo" },
	{ to: "/teacher", label: "Área docente" },
];

const Header = () => {
	const [isMenuOpen, setIsMenuOpen] = useState(false);

	return (
		<header className={styles.container}>
			<div className={styles.appName}>
				<h1>Alimenta</h1>
				<h4>Forma</h4>
			</div>
			<button
				className={styles.hamburger}
				onClick={() => setIsMenuOpen((currentState) => !currentState)}
				aria-label={isMenuOpen ? "Cerrar menú" : "Abrir menú"}
				aria-expanded={isMenuOpen}
				aria-controls={MENU_ID}
				type="button"
			>
				{isMenuOpen ? (
					<FaTimes className={styles.icon} aria-hidden="true" />
				) : (
					<FaBars className={styles.icon} aria-hidden="true" />
				)}
			</button>
			<nav aria-label="Navegación principal">
				<ul id={MENU_ID} className={isMenuOpen ? styles.menuActive : styles.menu}>
					{navigationItems.map(({ to, label, end }) => (
						<li key={to}>
							<NavLink to={to} end={end}>{label}</NavLink>
						</li>
					))}
				</ul>
			</nav>
		</header>
	);
};

export default Header;
