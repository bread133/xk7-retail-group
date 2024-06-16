export interface IFile {
  id: string
  name: string
  size: number
  type: string
  error?: boolean
  previewUrl?: string
  progress: number
  currentFile: File
  isSuccess?: boolean
}

export interface IVideoBorrowing {
  title_license: string
  title_piracy: string
  time_license_start: number
  time_license_finish: number
  time_piracy_start: number
  time_piracy_finish: number
}

export interface IResponseServerUploadFiles {
  message: string
  status: number
  borrowing: IVideoBorrowing[]
}
