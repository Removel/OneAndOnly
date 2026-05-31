export {}

declare global {
  type PixiLive2DModelInstance = {
    internalModel?: {
      width?: number
      height?: number
      renderer?: any
      textures?: Array<{
        baseTexture?: {
          valid?: boolean
          once: (event: 'loaded' | 'error', handler: (...args: unknown[]) => void) => void
        }
      }>
    }
    width?: number
    height?: number
    scale: { set: (value: number) => void }
    anchor: { set: (x: number, y?: number) => void }
    x: number
    y: number
    interactive: boolean
    cursor: string
    expression: (name: string) => void
    destroy: (options?: { children?: boolean; texture?: boolean; baseTexture?: boolean }) => void
    focus: (x: number, y: number, instant?: boolean) => void
    hasMotion: (name: string) => boolean
    internalModel?: any
  }

  type PixiApplicationInstance = {
    renderer: {
      width: number
      height: number
      resolution?: number
      resize: (width: number, height: number) => void
    }
    stage: {
      addChild: (child: PixiLive2DModelInstance) => void
      removeChild: (child: PixiLive2DModelInstance) => void
    }
    destroy: (
      removeView?: boolean,
      options?: { children?: boolean; texture?: boolean; baseTexture?: boolean },
    ) => void
  }

  interface Window {
    PIXI?: {
      Application: new (options: Record<string, unknown>) => PixiApplicationInstance
      live2d?: {
        Live2DModel?: {
          from: (entry: string, options?: Record<string, unknown>) => Promise<PixiLive2DModelInstance>
        }
      }
    }
    Live2DCubismCore?: unknown
  }
}
