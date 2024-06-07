export interface IFile {
  id: string
  name: string
  size: number
  type: string
  error?: boolean
  previewUrl?: string
  progress: number
  currentFile: File
}

export interface IVideoBorrowing {
  originalLink: string
  id: string
  start: string
  end: string
  nameVideo: string
}

export interface IResponseServerUploadFiles {
  message: string
  status: number
  borrowing: IVideoBorrowing[]
}
