import { useCallback } from "react";
import Header from "../components/Header";
import Title from "../components/Title";
import CourseCard from "../components/CourseCard";
import AsyncState from "../components/AsyncState";
import useRemoteResource from "../hooks/useRemoteResource";
import { getCourses } from "../services/coursesApi";

const Courses = () => {
	const loadCourses = useCallback(() => getCourses(), []);
	const { data: courses, error, loading, reload } = useRemoteResource(loadCourses);
	return (
		<div>
			<Header />
			<Title text="Nuestros Cursos" />
			<AsyncState loading={loading} error={error} empty={courses?.length === 0} emptyMessage="No hay cursos disponibles." onRetry={reload}>
				<section aria-label="Cursos disponibles">
					{courses?.map((course) => <CourseCard key={course.id} course={course} />)}
				</section>
			</AsyncState>
		</div>		
	)
}

export default Courses;
