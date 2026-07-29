import styles from "./TextCard.module.css";

const AboutText = () => {
  return (
		<section className={styles.container} aria-labelledby="about-text-title">
			<h2 id="about-text-title">Formación que mejora el trabajo diario</h2>
			<p>En Alimenta Forma acercamos formación práctica y actualizada a quienes trabajan en alimentación y hostelería. Nuestros itinerarios abarcan manipulación y seguridad alimentaria, alérgenos, nutrición, cocina, sala, bar y gestión hostelera.</p>
			<p>Diseñamos experiencias presenciales, online y mixtas para que cada profesional pueda aplicar lo aprendido en su puesto, avanzar en su carrera y acreditar sus competencias.</p>
		</section>
	)
}

export default AboutText;
