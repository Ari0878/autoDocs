import os
from typing import Optional
from openai import OpenAI


class AIEnhancer:
    """
    Mejora la documentación técnica usando IA (OpenAI GPT).
    Genera descripciones más detalladas, explica patrones de diseño,
    y proporciona insights técnicos avanzados.
    """

    def __init__(self):
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)

    def is_available(self) -> bool:
        """Verifica si la API de OpenAI está configurada y disponible."""
        return self.client is not None and self.api_key

    def enhance_function_description(self, function: dict, context: str = "") -> str:
        """
        Genera una descripción mejorada para una función usando IA.
        
        Args:
            function: Diccionario con información de la función
            context: Contexto adicional del proyecto
            
        Returns:
            Descripción mejorada de la función
        """
        if not self.is_available():
            return function.get('docstring', '') or f"Función {function['name']}"
        
        try:
            params = ', '.join(function.get('params', []))
            prompt = f"""Analiza esta función y genera una descripción técnica profesional:

Nombre: {function['name']}
Parámetros: {params}
Archivo: {function.get('file', 'desconocido')}
Docstring existente: {function.get('docstring', 'ninguna')}
Contexto del proyecto: {context}

Genera una descripción que incluya:
1. Propósito de la función
2. Qué parámetros recibe y su función
3. Qué retorna (si es inferible)
4. Casos de uso típicos
5. Notas importantes sobre su implementación

Mantén la descripción concisa pero técnica (máximo 150 palabras)."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en documentación técnica de software. Genera descripciones claras, precisas y técnicas."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AI] Error al mejorar descripción de función: {e}")
            return function.get('docstring', '') or f"Función {function['name']}"

    def enhance_class_description(self, class_info: dict, context: str = "") -> str:
        """
        Genera una descripción mejorada para una clase usando IA.
        
        Args:
            class_info: Diccionario con información de la clase
            context: Contexto adicional del proyecto
            
        Returns:
            Descripción mejorada de la clase
        """
        if not self.is_available():
            return class_info.get('docstring', '') or f"Clase {class_info['name']}"
        
        try:
            methods = ', '.join(class_info.get('methods', [])[:10])
            bases = ', '.join(class_info.get('bases', []))
            
            prompt = f"""Analiza esta clase y genera una descripción técnica profesional:

Nombre: {class_info['name']}
Hereda de: {bases or 'object'}
Métodos: {methods}
Archivo: {class_info.get('file', 'desconocido')}
Docstring existente: {class_info.get('docstring', 'ninguna')}
Contexto del proyecto: {context}

Genera una descripción que incluya:
1. Propósito y responsabilidad de la clase
2. Patrones de diseño que implementa (si aplica)
3. Relación con otras clases (herencia, composición)
4. Métodos principales y su función
5. Casos de uso típicos

Mantén la descripción concisa pero técnica (máximo 150 palabras)."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en documentación técnica de software. Genera descripciones claras, precisas y técnicas."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AI] Error al mejorar descripción de clase: {e}")
            return class_info.get('docstring', '') or f"Clase {class_info['name']}"

    def enhance_endpoint_description(self, endpoint: dict, context: str = "") -> str:
        """
        Genera una descripción mejorada para un endpoint de API usando IA.
        
        Args:
            endpoint: Diccionario con información del endpoint
            context: Contexto adicional del proyecto
            
        Returns:
            Descripción mejorada del endpoint
        """
        if not self.is_available():
            return f"Endpoint {endpoint.get('method')} {endpoint.get('path')}"
        
        try:
            prompt = f"""Analiza este endpoint de API y genera una descripción técnica profesional:

Método: {endpoint.get('method')}
Ruta: {endpoint.get('path')}
Framework: {endpoint.get('framework', 'desconocido')}
Archivo: {endpoint.get('file', 'desconocido')}
Contexto del proyecto: {context}

Genera una descripción que incluya:
1. Propósito del endpoint
2. Qué recursos manipula
3. Parámetros esperados (query params, body, headers)
4. Respuestas típicas y códigos de estado
5. Casos de uso y consideraciones de seguridad

Mantén la descripción concisa pero técnica (máximo 150 palabras)."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en documentación de APIs REST. Genera descripciones claras, precisas y técnicas."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AI] Error al mejorar descripción de endpoint: {e}")
            return f"Endpoint {endpoint.get('method')} {endpoint.get('path')}"

    def generate_architecture_insights(self, analysis_results: dict) -> str:
        """
        Genera insights sobre la arquitectura del proyecto usando IA.
        
        Args:
            analysis_results: Resultados del análisis del proyecto
            
        Returns:
            Insights sobre arquitectura y patrones detectados
        """
        if not self.is_available():
            return "Insights de IA no disponibles - configura OPENAI_API_KEY"
        
        try:
            lang = analysis_results.get('primary_language', 'desconocido')
            langs = analysis_results.get('languages', {})
            functions = analysis_results.get('functions', [])
            classes = analysis_results.get('classes', [])
            endpoints = analysis_results.get('endpoints', [])
            
            prompt = f"""Analiza esta información de un proyecto de software y genera insights arquitectónicos:

Lenguaje principal: {lang}
Lenguajes detectados: {langs}
Total funciones: {len(functions)}
Total clases: {len(classes)}
Total endpoints: {len(endpoints)}

Genera insights sobre:
1. Patrones arquitectónicos probables (MVC, Microservicios, Monolito, etc.)
2. Buenas prácticas detectadas
3. Áreas de mejora sugeridas
4. Complejidad del proyecto
5. Recomendaciones de escalabilidad

Mantén los insights concisos y accionables (máximo 200 palabras)."""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un arquitecto de software senior. Genera insights técnicos y prácticos sobre arquitectura de proyectos."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AI] Error al generar insights de arquitectura: {e}")
            return "No se pudieron generar insights de arquitectura"

    def enhance_documentation(self, analysis_results: dict) -> dict:
        """
        Mejora toda la documentación del proyecto usando IA.
        
        Args:
            analysis_results: Resultados del análisis del proyecto
            
        Returns:
            Resultados con descripciones mejoradas por IA
        """
        if not self.is_available():
            print("[AI] OpenAI no configurado, usando documentación básica")
            return analysis_results
        
        print("[AI] Mejorando documentación con IA...")
        
        # Contexto del proyecto
        context = f"Proyecto en {analysis_results.get('primary_language', 'desconocido')} con {len(analysis_results.get('functions', []))} funciones"
        
        # Mejorar funciones
        for func in analysis_results.get('functions', [])[:20]:  # Limitar a 20 para no exceder límites
            if not func.get('docstring'):
                func['ai_description'] = self.enhance_function_description(func, context)
        
        # Mejorar clases
        for cls in analysis_results.get('classes', [])[:15]:
            if not cls.get('docstring'):
                cls['ai_description'] = self.enhance_class_description(cls, context)
        
        # Mejorar endpoints
        for ep in analysis_results.get('endpoints', [])[:15]:
            ep['ai_description'] = self.enhance_endpoint_description(ep, context)
        
        # Generar insights de arquitectura
        analysis_results['ai_architecture_insights'] = self.generate_architecture_insights(analysis_results)
        
        print("[AI] Documentación mejorada exitosamente")
        return analysis_results
