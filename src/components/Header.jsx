import { useState } from "react";
import { Link } from "react-router-dom";
import styles from "./HeaderStyles.module.css"
import { FaBars, FaTimes } from "react-icons/fa";

const Header = () => {

	const [click, setClick] = useState(false);
	const handleClick = () => {
		
		setClick(!click);
	}

	return (
		<header className={styles.container} >
			<div className={styles.appName} >
				<h1>Alimenta</h1>
				<h4>Forma</h4>
			</div>
			<nav aria-label="Navegación principal">
				<ul className={click ? `${styles.menuActive}` : `${styles.menu}`} >
					<li>
						<Link to={'/'}>Inicio</Link>
					</li>
					<li>
						<Link to={'/courses'}>Nuestros Cursos</Link>
					</li>
					<li>
						<Link to={'/membership'}>Nuestros Precios</Link>
					</li>
					<li>
						<Link to={'/about'}>Acerca de</Link>
					</li>
					<li>
						<Link to={'/faqs'}>Preguntas Frecuentes</Link>
					</li>
					<li><Link to={'/coorp'}>Empresas</Link></li>
					<li><Link to={'/jobs'}>Empleo</Link></li>
					<li><Link to={'/teacher'}>Área docente</Link></li>
				</ul>
			</nav>
			<button className={styles.hamburger} onClick={handleClick} aria-label={click ? "Cerrar menú" : "Abrir menú"} aria-expanded={click} type="button">
				{click ? (
						<FaTimes className={styles.icon} />
					) : (
						<FaBars className={styles.icon} />
					)
				}
			</button>
		</header>
	)
}

export default Header;
