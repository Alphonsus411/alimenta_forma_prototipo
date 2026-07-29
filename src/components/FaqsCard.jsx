import styles from "./FaqsCard.module.css"

const FaqsCard = () => {
	return (
		<section className={styles.container} aria-label="Dudas habituales sobre la formación">
			<article>
				<h2>¿Qué formación puedo encontrar?</h2>
				<p>Ofrecemos cursos de manipulación y seguridad alimentaria, alérgenos, nutrición, cocina, sala, bar y gestión hostelera.</p>
			</article>
			<article>
				<h2>¿Qué modalidades están disponibles?</h2>
				<p>Cada ficha indica si la formación es presencial, online o mixta, además de sus fechas, duración, requisitos y criterios de aprobación.</p>
			</article>
			<article>
				<h2>¿Cómo obtengo mi certificado?</h2>
				<p>Cuando completes un curso y cumplas sus criterios de evaluación y asistencia, podrás obtener el certificado correspondiente una vez cerrado el curso.</p>
			</article>
			<article>
				<h2>¿Puede una empresa formar a su plantilla?</h2>
				<p>Sí. Preparamos planes adaptados y facilitamos el seguimiento de las inscripciones, respetando siempre la privacidad de cada participante.</p>
			</article>
		</section>
	)
}

export default FaqsCard;
