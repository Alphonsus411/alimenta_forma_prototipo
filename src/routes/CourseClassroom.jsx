import { useCallback } from "react";
import { Link, useParams } from "react-router-dom";
import AsyncState from "../components/AsyncState";
import Header from "../components/Header";
import useRemoteResource from "../hooks/useRemoteResource";
import { getCurrentUser } from "../services/authApi";
import { getContent } from "../services/contentApi";
import { getCourse } from "../services/coursesApi";
import { getRegistrations } from "../services/registrationsApi";
import styles from "./StudentRoutes.module.css";

const CourseClassroom = () => {
  const { courseId } = useParams();
  const load = useCallback(async () => {
    await getCurrentUser();
    const [course, registrations] = await Promise.all([getCourse(courseId), getRegistrations()]);
    if (!registrations.some((item) => String(item.course) === String(courseId))) {
      const denied = new Error("No tienes permisos para acceder al aula de este curso.");
      denied.status = 403;
      throw denied;
    }
    return { course, content: course.content ? await getContent(course.content) : null };
  }, [courseId]);
  const { data, error, loading, reload } = useRemoteResource(load);
  const anonymous = error?.status === 401 || (error?.status === 403 && error.message !== "No tienes permisos para acceder al aula de este curso.");

  return <><Header /><main className={styles.main}><h1>Aula del curso</h1>
    {anonymous ? <div role="alert"><p>Debes iniciar sesión para acceder al aula.</p><Link to="/login">Iniciar sesión</Link></div> :
      <AsyncState loading={loading} error={error} empty={data && !data.content} emptyMessage="Todavía no hay contenidos disponibles." onRetry={reload}>
        {data?.content && <article className={styles.card}>
          <h2>{data.course.title}</h2><h3>{data.content.title}</h3><p>{data.content.comment}</p>
          <ul className={styles.meta}>
            {data.content.doc && <li><a href={data.content.doc}>Descargar documento</a></li>}
            {data.content.videos && <li><a href={data.content.videos}>Ver vídeo</a></li>}
            {data.content.img && <li><a href={data.content.img}>Ver material gráfico</a></li>}
          </ul>
        </article>}
      </AsyncState>}
  </main></>;
};

export default CourseClassroom;
