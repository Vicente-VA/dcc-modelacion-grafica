from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
from PIL import Image

from grafica_tarea.gpu_shape import GPUShape

SIZE_IN_BYTES = 4


def textureSimpleSetup(imgName, sWrapMode, tWrapMode, minFilterMode, maxFilterMode):
     # wrapMode: GL_REPEAT, GL_CLAMP_TO_EDGE
     # filterMode: GL_LINEAR, GL_NEAREST
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, sWrapMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, tWrapMode)

    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minFilterMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, maxFilterMode)

    image = Image.open(imgName)
    img_data = np.array(image, np.uint8)

    if image.mode == "RGB":
        internalFormat = GL_RGB
        format = GL_RGB
    elif image.mode == "RGBA":
        internalFormat = GL_RGBA
        format = GL_RGBA
    else:
        print("Image mode not supported.")
        raise Exception()

    glTexImage2D(GL_TEXTURE_2D, 0, internalFormat, image.size[0], image.size[1], 0, format, GL_UNSIGNED_BYTE, img_data)

    return texture


class SimpleTextureTransformShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 330

            uniform mat4 transform;

            in vec3 position;
            in vec2 texCoords;

            out vec2 outTexCoords;

            void main()
            {
                gl_Position = transform * vec4(position, 1.0f);
                outTexCoords = texCoords;
            }
            """

        fragment_shader = """
            #version 330

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D samplerTex;

            void main()
            {
                outColor = texture(samplerTex, outTexCoords);
            }
            """

        # Binding artificial vertex array object for validation
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)


        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + 2d texture coordinates => 3*4 + 2*4 = 20 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(3 * SIZE_IN_BYTES))
        glEnableVertexAttribArray(texCoords)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)


class SimpleTextureModelViewProjectionShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 330

            uniform mat4 projection;
            uniform mat4 view;
            uniform mat4 model;

            in vec3 position;
            in vec2 texCoords;

            out vec2 outTexCoords;

            void main()
            {
                gl_Position = projection * view * model * vec4(position, 1.0f);
                outTexCoords = texCoords;
            }
            """

        fragment_shader = """
            #version 330

            uniform sampler2D samplerTex;

            in vec2 outTexCoords;

            out vec4 outColor;

            void main()
            {
                outColor = texture(samplerTex, outTexCoords);
            }
            """

        # Binding artificial vertex array object for validation
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)


        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + 2d texture coordinates => 3*4 + 2*4 = 20 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(12))
        glEnableVertexAttribArray(texCoords)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)


class SimpleTextureModelViewProjectionShaderProgramOBJ:

    def __init__(self):

        vertex_shader = """
            #version 330
            in vec3 position;
            in vec2 texCoords;
            in vec3 normal;
            out vec2 fragTexCoords;
            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 projection;

            void main()
            {
                vec3 vertexPos = vec3(model * vec4(position, 1.0));
                gl_Position = projection * view * vec4(vertexPos, 1.0);
                fragTexCoords = vec2(texCoords[1], texCoords[0]);

                vec3 normals = normal; // No hace nada
            }
            """

        fragment_shader = """
            #version 330
            in vec2 fragTexCoords;
            out vec4 fragColor;
            uniform sampler2D samplerTex;
            void main()
            {
                vec4 textureColor = texture(samplerTex, fragTexCoords);
                fragColor = textureColor;
            }
            """

        # Binding artificial vertex array object for validation
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)


        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + rgb color + 3d normals => 3*4 + 2*4 + 3*4 = 32 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(color, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        normal = glGetAttribLocation(self.shaderProgram, "normal")
        if normal >= 0: 
            glVertexAttribPointer(normal, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))
            glEnableVertexAttribArray(normal)

        

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(gpuShape.vao)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)
