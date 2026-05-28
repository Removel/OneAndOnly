import type { Plugin } from 'vite'
import fs from 'node:fs'
import path from 'node:path'

/**
 * Vite 插件：处理 Live2D 模型纹理路径
 *
 * 问题：Live2D 官方示例模型把纹理放在子目录（如 mao_pro.4096/），
 * 但 model3.json 中引用的是相对路径 "texture_00.png"。
 *
 * 解决方案：拦截 .model3.json 请求，动态重写 Textures 路径，
 * 指向实际存在的纹理文件。
 */
export function live2dTexturePlugin(): Plugin {
  let publicDir = ''

  return {
    name: 'vite-plugin-live2d-texture',
    configResolved(config) {
      publicDir = config.publicDir
    },
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        if (!req.url?.endsWith('.model3.json')) {
          return next()
        }

        const filePath = path.join(server.config.publicDir, req.url)
        if (!fs.existsSync(filePath)) {
          return next()
        }

        try {
          const json = rewriteModelTextures(filePath)
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify(json))
        } catch (err) {
          console.error('[live2d-texture-plugin] Error processing model3.json:', err)
          next()
        }
      })
    },
    writeBundle(options) {
      if (!options.dir) return

      const live2dDir = path.join(options.dir, 'live2d')
      if (!fs.existsSync(live2dDir)) return

      for (const filePath of walk(live2dDir)) {
        if (!filePath.endsWith('.model3.json')) continue
        rewriteModelTexturesInPlace(filePath)
      }
    },
  }
}

function rewriteModelTextures(filePath: string): unknown {
  const content = fs.readFileSync(filePath, 'utf-8')
  const json = JSON.parse(content)

  if (json.FileReferences?.Textures) {
    const modelDir = path.dirname(filePath)
    const modelName = path.basename(filePath, '.model3.json')

    json.FileReferences.Textures = json.FileReferences.Textures.map((texPath: string) => {
      const directPath = path.join(modelDir, texPath)
      if (fs.existsSync(directPath)) return texPath

      const resolutions = ['4096', '2048', '1024', '512']
      for (const res of resolutions) {
        const subDir = `${modelName}.${res}`
        const subPath = path.join(modelDir, subDir, texPath)
        if (fs.existsSync(subPath)) return `${subDir}/${texPath}`
      }

      return texPath
    })
  }

  return json
}

function rewriteModelTexturesInPlace(filePath: string) {
  const before = fs.readFileSync(filePath, 'utf-8')
  const after = `${JSON.stringify(rewriteModelTextures(filePath), null, 2)}\n`
  if (before !== after) fs.writeFileSync(filePath, after, 'utf-8')
}

function walk(dir: string): string[] {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const fullPath = path.join(dir, entry.name)
    return entry.isDirectory() ? walk(fullPath) : [fullPath]
  })
}
