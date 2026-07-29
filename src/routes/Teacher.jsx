import { Link } from "react-router-dom";
import Header from "../components/Header";
import styles from "./InfoRoute.module.css";

const Teacher = () => {
    return (
		<>
			<Header />
			<main className={styles.main}>
				<h1>Área docente</h1>
				<p className={styles.intro}>El espacio de trabajo para preparar, impartir y evaluar la formación asignada. Las acciones disponibles dependen de tu cuenta y se limitan a tus cursos.</p>
				<section aria-labelledby="teacher-workflow-title">
					<h2 id="teacher-workflow-title">Tu ciclo de trabajo</h2>
					<ol className={styles.steps}>
						<li><strong>Prepara el curso:</strong> completa la ficha, ordena contenidos y actividades y solicita su revisión.</li>
						<li><strong>Acompaña al grupo:</strong> consulta las matrículas autorizadas y facilita los contenidos previstos.</li>
						<li><strong>Registra evidencias:</strong> incorpora asistencia, actividades, notas y retroalimentación.</li>
						<li><strong>Propón la finalización:</strong> revisa los resultados antes de que administración cierre el curso.</li>
					</ol>
				</section>
				<p>Inicia sesión para acceder a las funciones habilitadas para tu perfil docente.</p>
				<Link className={styles.cta} to="/login">Acceder como docente</Link>
			</main>
		</>
    )
}

export default Teacher;
