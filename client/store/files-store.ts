import { AxiosError } from 'axios'
import { toast } from 'react-toastify'
import { devtools } from 'zustand/middleware'
import { create } from 'zustand'
import { v4 as uuidv4 } from 'uuid'

import { IFile, IResponseServerUploadFiles } from '@/types/index'
import { uploadFile } from '@/services/api'
import { MAX_N_FILES_TO_UPLOAD } from '@/consts'
import { validateFileSize, validateFileType } from '@/lib/utils'
import { useBorrowingStore } from '@/store/borrowing-store'

interface FilesState {
  filesZus: IFile[]
  isLoading: boolean
  errors: string[]
  add: (fileList: FileList) => void
  setProgress: (fileId: string, progress: number) => void
}

export const useFilesStore = create<FilesState>()(
  devtools((set, get) => ({
    filesZus: [],
    isLoading: false,
    errors: [],

    add: async (fileList) => {
      const files: File[] = Array.from(fileList)
      const { filesZus, setProgress } = get()
      const newErrors: string[] = []

      // проверяем количество
      if (filesZus.length + files.length > MAX_N_FILES_TO_UPLOAD) {
        const message = `Слишком много файлов. Одновременно можно загрузить не более ${MAX_N_FILES_TO_UPLOAD}.`
        newErrors.push(message)
      }

      // проверяем тип файла и размер файла
      for (const file of files) {
        if (!validateFileType(file)) {
          const message = `Неверный тип файла. Пожалуйста, загрузите файл допустимого типа.`
          newErrors.push(message)
        }

        if (!validateFileSize(file)) {
          const message = `Файл слишком большой.`
          newErrors.push(message)
        }

        if (newErrors.length > 0) {
          break
        }
      }

      if (newErrors.length > 0) {
        newErrors.forEach((error) => toast.error(error))
        set((state) => ({ errors: [...state.errors, ...newErrors] }))
        return
      }

      // Если ошибок нет, очищаем массив ошибок и загружаем файлы
      const transformedFiles = transformFiles(files)
      set((state) => ({
        filesZus: [...state.filesZus, ...transformedFiles],
        errors: []
      }))

      set({ isLoading: true })
      try {
        const data: IResponseServerUploadFiles[] = await uploadFilesAll(
          transformedFiles,
          setProgress
        )

        // Добавляем данные из IResponseServerUploadFiles в другое хранилище
        data.forEach((item) => {
          useBorrowingStore.getState().addVideoBorrowings(item.borrowing)
        })

        toast.success('Все файлы успешно загружены')
      } catch (error) {
        // убрать лишние файлы с ошибкой, хотя  можно и другую логику добавить
        if (error instanceof AxiosError) {
          toast.error(error.message)
          set((state) => ({
            filesZus: state.filesZus.filter(
              (file) =>
                !transformedFiles.some((newFile) => newFile.id === file.id)
            )
          }))
          return
        }
      } finally {
        set({ isLoading: false })
      }
    },

    setProgress: (fileId: string, progress: number) => {
      set((state) => ({
        filesZus: state.filesZus.map((file) =>
          file.id === fileId ? { ...file, progress } : file
        )
      }))
    },

    setIsSuccess: (fileId: string, isSuccess: boolean) => {
      set((state) => ({
        filesZus: state.filesZus.map((file) =>
          file.id === fileId ? { ...file, isSuccess } : file
        )
      }))
    }
  }))
)

// вспомогательные функции

const uploadFilesAll = async (
  validFiles: IFile[],
  setProgress: (fileId: string, progress: number) => void
) => {
  const uploadPromises = validFiles.map(async (file) => {
    return await uploadFile({
      file,
      fileId: file.id,
      setProgress,
      url: '/files'
    })
  })
  return await Promise.all(uploadPromises)
}

const transformFiles = (validFiles: File[]): IFile[] => {
  return validFiles.map((file) => ({
    id: uuidv4(),
    name: file.name,
    size: file.size,
    type: file.type,
    error: false,
    previewUrl: URL.createObjectURL(file),
    progress: 0,
    currentFile: file
  }))
}
