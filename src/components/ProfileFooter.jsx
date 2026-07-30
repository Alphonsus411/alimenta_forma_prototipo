import { Link } from "react-router-dom";
import { FaHome, FaUserCircle, FaClipboardList, FaIdBadge } from "react-icons/fa";
import styles from "./ProfileFooter.module.css";

const profileLinks = [
	{ to: "/", label: "Inicio", Icon: FaHome },
	{ to: "/login", label: "Identificarse", Icon: FaIdBadge },
	{ to: "/student", label: "Mi progreso", Icon: FaClipboardList },
	{ to: "/profile", label: "Mi perfil", Icon: FaUserCircle },
];

const ProfileFooter = () => {
	return (
		<nav className={styles.container} aria-label="Navegación del perfil">
			{profileLinks.map(({ to, label, Icon }) => (
				<Link key={to} to={to}>
					<Icon aria-hidden="true" focusable="false" />
					<span className={styles.visuallyHidden}>{label}</span>
				</Link>
			))}
		</nav>
	)
}

export default ProfileFooter;
