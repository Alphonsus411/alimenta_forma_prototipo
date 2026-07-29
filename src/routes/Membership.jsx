import Header from "../components/Header";
import Title from "../components/Title";
import MembershipCard from "../components/MembershipCard";

const Membership = () => {

	

	return (
		<div>
			<Header />
			<Title text="Nuestros Precios" />
			<MembershipCard type="Estudiante" detail="Acceso a los cursos disponibles." />
		</div>
	)
}

export default Membership;
