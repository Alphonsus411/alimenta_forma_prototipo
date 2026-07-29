import Header from "../components/Header";
import styles from "./InfoRoute.module.css";

const Coorp = () => {
	return (
		<>
			<Header />
			<main className={styles.main}>
				<h1>Formación para empresas</h1>
				<p className={styles.intro}>Impulsa las competencias de tu plantilla con un plan adaptado a la actividad, los puestos y los objetivos de tu negocio hostelero o alimentario.</p>
				<section aria-labelledby="company-services-title">
					<h2 id="company-services-title">Una propuesta integral</h2>
					<div className={styles.grid}>
						<article className={styles.card}><h3>Planes de formación</h3><p>Detectamos necesidades y combinamos cursos presenciales, online o mixtos en un itinerario ajustado a cada equipo.</p></article>
						<article className={styles.card}><h3>Cumplimiento normativo</h3><p>Reforzamos conocimientos de higiene, APPCC, trazabilidad, alérgenos y prácticas seguras para facilitar su aplicación diaria.</p></article>
						<article className={styles.card}><h3>Seguimiento de plantilla</h3><p>Centraliza inscripciones y consulta el avance autorizado, respetando la privacidad y el acceso mínimo a los datos de aprendizaje.</p></article>
					</div>
				</section>
				<section aria-labelledby="company-contact-title">
					<h2 id="company-contact-title">Cuéntanos qué necesita tu equipo</h2>
					<p>Contacta con el equipo comercial para preparar una propuesta sin compromiso.</p>
					<a className={styles.cta} href="mailto:empresas@alimentaforma.es?subject=Plan%20de%20formaci%C3%B3n%20para%20empresa">Solicitar propuesta comercial</a>
				</section>
			</main>
		</>
	)
}

export default Coorp;
