import Header from "../components/Header";
import styles from "./InfoRoute.module.css";

const Jobs = () => {
    return (
		<>
			<Header />
			<main className={styles.main}>
				<h1>Oportunidades profesionales</h1>
				<p className={styles.intro}>Conectamos talento formado con empresas de alimentación y hostelería. Este espacio está dirigido tanto a profesionales como a organizaciones que quieren incorporar personas preparadas.</p>
				<section aria-labelledby="job-areas-title">
					<h2 id="job-areas-title">Áreas profesionales</h2>
					<ul className={styles.grid}>
						<li className={styles.card}><h3>Cocina y producción</h3><p>Cocina, apoyo de producción, panadería y operaciones alimentarias.</p></li>
						<li className={styles.card}><h3>Sala y bar</h3><p>Servicio, atención al cliente, cafetería, coctelería y coordinación de sala.</p></li>
						<li className={styles.card}><h3>Calidad y gestión</h3><p>Seguridad alimentaria, control de alérgenos, compras y gestión hostelera.</p></li>
					</ul>
				</section>
				<section aria-labelledby="job-contact-title">
					<h2 id="job-contact-title">Participa en nuestra bolsa de talento</h2>
					<p>Si buscas una oportunidad o quieres publicar una oferta, escríbenos indicando tu perfil o las características del puesto.</p>
					<a className={styles.cta} href="mailto:empleo@alimentaforma.es?subject=Bolsa%20de%20talento">Contactar con empleo</a>
				</section>
			</main>
		</>
    )
}

export default Jobs;
