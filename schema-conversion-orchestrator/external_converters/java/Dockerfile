# java-converter/Dockerfile
FROM eclipse-temurin:17-jdk as build

WORKDIR /app
COPY pom.xml .
COPY src ./src

RUN ./mvnw package -DskipTests

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/java-converter-0.0.1-SNAPSHOT.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]
