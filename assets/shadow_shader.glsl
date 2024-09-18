#define MAX_LIGHTS 100
#define N 100

uniform vec2 lightPositions[MAX_LIGHTS];
uniform float lightSize;

float terrain(vec2 samplePoint) {
    return texture(iChannel0, samplePoint).a;
}

float castRay(vec2 from, vec2 to) {
    float opacitySum = 0.0;
    float totalDistance = distance(from, to);
    float N_float = float(N);
    for (float i = 0.0; i <= N_float; i++) {
        float t = i / N_float;
        vec2 samplePoint = mix(from, to, t);
        float terrainOpacity = terrain(samplePoint);
        opacitySum += terrainOpacity / N_float;
    }
    float attenuationCoefficient = 3.0;
    float lightAmount = exp(-attenuationCoefficient * opacitySum);
    return lightAmount;
}

void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = fragCoord / iResolution.xy;
    vec4 sceneColor = texture(iChannel1, uv);

    float totalLight = 0.0;

    for (int i = 0; i < MAX_LIGHTS; i++) {
        if (lightPositions[i] == vec2(0.0)) break;

        vec2 normalizedLightPos = lightPositions[i] / iResolution.xy;
        float distanceToLight = length(normalizedLightPos - uv);

        if (distanceToLight < lightSize / iResolution.x) {
            float lightAmount = castRay(uv, normalizedLightPos);
            lightAmount *= 1.0 - smoothstep(0.0, lightSize / iResolution.x, distanceToLight);
            totalLight += lightAmount;
        }
    }

    totalLight = clamp(totalLight, 0.0, 1.0);

    vec3 litColor = sceneColor.rgb * (totalLight * 0.8 + 0.2);
    fragColor = vec4(litColor, sceneColor.a);
}
