'use client'

import {
  forwardRef,
  useCallback,
  useState,
  type ChangeEvent,
  type DragEvent
} from 'react'

import {
  ALLOWED_FILE_TYPES,
  MAX_FILE_SIZE,
  MAX_N_FILES_TO_UPLOAD
} from '@/consts'
import { cn } from '@/lib/utils'
import PlusIcon from '@/assets/plus.svg'
import { VideoUpload } from '@/components/video-upload'
import { IFile } from '@/types'
import { useFilesStore } from '@/store/files-store'

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {}

export const FileInput = forwardRef<HTMLInputElement, InputProps>(
  ({ className, ...props }, ref) => {
    const { add, filesZus, isLoading } = useFilesStore()

    const [dragActive, setDragActive] = useState<boolean>(false)

    const noInput = filesZus.length === 0

    // обрабатываем события перетаскивания
    const handleDrag = useCallback(
      (event: DragEvent<HTMLFormElement | HTMLDivElement>) => {
        event.preventDefault()
        event.stopPropagation()
        setDragActive(event.type === 'dragenter' || event.type === 'dragover')
      },
      []
    )

    // срабатывает, когда файл выбран щелчком мыши
    const handleChange = useCallback(
      async (event: ChangeEvent<HTMLInputElement>) => {
        event.preventDefault()
        if (event.target.files && event.target.files[0]) {
          add(event.target.files)
        }
      },
      [add]
    )

    // срабатывает при dropped
    const handleDrop = useCallback(
      (event: DragEvent<HTMLDivElement>) => {
        event.preventDefault()
        event.stopPropagation()
        if (event.dataTransfer.files && event.dataTransfer.files[0]) {
          setDragActive(false)
          add(event.dataTransfer.files)
          event.dataTransfer.clearData()
        }
      },
      [add]
    )

    return (
      <form
        onSubmit={(e) => e.preventDefault()}
        onDragEnter={handleDrag}
        className='flex h-full items-center w-full lg:w-2/3 justify-start'
      >
        <label
          htmlFor='dropzone-file'
          className={cn(
            'group relative h-full flex flex-col items-center justify-center w-full aspect-video border-2 border-slate-300 border-dashed rounded-lg dark:border-gray-600 transition',
            { 'dark:border-slate-400 dark:bg-slate-200': dragActive },
            { 'h-fit aspect-auto': !noInput },
            { 'items-start justify-start': !noInput },
            { 'dark:hover:border-gray-500 dark:hover:bg-slate-200': noInput }
          )}
        >
          <div
            className={cn(
              'relative w-full h-full flex flex-col items-center justify-center',
              { 'items-start': !noInput }
            )}
          >
            {noInput ? (
              <>
                <div
                  className='absolute inset-0 cursor-pointer'
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  style={{ pointerEvents: isLoading ? 'none' : 'auto' }}
                />

                <svg
                  aria-hidden='true'
                  className='w-10 h-10 mb-3 text-gray-400'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                  xmlns='http://www.w3.org/2000/svg'
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth='2'
                    d='M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12'
                  ></path>
                </svg>

                <p className='mb-2 text-sm text-gray-500 dark:text-gray-400'>
                  <span className='font-semibold'>
                    Нажмите, чтобы загрузить
                  </span>{' '}
                  или перетащите
                </p>
                <p className='text-xs text-gray-500 dark:text-gray-400'>
                  до {MAX_N_FILES_TO_UPLOAD} видео, до{' '}
                  {(MAX_FILE_SIZE / 1000000000).toFixed(0)} ГБ каждый файл
                </p>

                <input
                  {...props}
                  ref={ref}
                  multiple
                  onChange={handleChange}
                  accept={ALLOWED_FILE_TYPES.join(',')}
                  id='dropzone-file'
                  type='file'
                  className='hidden'
                  disabled={isLoading}
                />
              </>
            ) : (
              <div className='flex flex-col w-full h-full'>
                <div className='overflow-x-auto sm:-mx-6 lg:-mx-8'>
                  <div className='align-middle inline-block min-w-full sm:px-6 lg:px-8'>
                    <div className='shadow overflow-hidden sm:rounded-lg'>
                      <table className='min-w-full divide-y dark:divide-slate-600'>
                        <thead className='bg-slate-800'>
                          <tr>
                            <th
                              scope='col'
                              className='px-6 py-3 text-left text-xs font-medium dark:text-slate-300  uppercase tracking-wider'
                            >
                              Preview
                            </th>
                            <th
                              scope='col'
                              className='px-6 py-3 text-left text-xs font-medium dark:text-slate-300  uppercase tracking-wider'
                            >
                              Name
                            </th>
                            <th
                              scope='col'
                              className='px-6 py-3 text-left text-xs font-medium dark:text-slate-300  uppercase tracking-wider'
                            >
                              Size
                            </th>
                            <th
                              scope='col'
                              className='px-6 py-3 text-left text-xs font-medium dark:text-slate-300  uppercase tracking-wider'
                            >
                              Status
                            </th>
                          </tr>
                        </thead>
                        <tbody className='relative divide-y dark:divide-slate-600'>
                          {filesZus.map((file: IFile) => {
                            return (
                              <VideoUpload
                                key={file.id}
                                error={file.error}
                                name={file.name}
                                size={file.size}
                                type={file.type}
                                progress={file.progress}
                              />
                            )
                          })}
                        </tbody>
                      </table>

                      <label
                        htmlFor='dropzone-file-images-present'
                        className='relative cursor-pointer group hover:border-gray-500 dark:hover:bg-slate-200 transition flex justify-center py-4 border-t border-slate-600'
                      >
                        <PlusIcon className='flex justify-center  items-center fill-slate-500 stroke-1 group-hover:fill-slate-400 ' />

                        <input
                          {...props}
                          ref={ref}
                          multiple
                          onChange={handleChange}
                          accept={ALLOWED_FILE_TYPES.join(',')}
                          type='file'
                          id='dropzone-file-images-present'
                          className='relative z-20 hidden'
                          disabled={isLoading}
                        />
                        <div
                          className='absolute inset-0'
                          onDragEnter={handleDrag}
                          onDragLeave={handleDrag}
                          onDragOver={handleDrag}
                          onDrop={handleDrop}
                          style={{ pointerEvents: isLoading ? 'none' : 'auto' }}
                        />
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </label>
      </form>
    )
  }
)

FileInput.displayName = 'FileInput'

// const { loading, error, fetchFiles } = useFiles(
//     (state) => ({
//       loading: state.loading,
//       error: state.error,
//       fetchFiles: state.fetchFiles,
//     }),
//     shallow
//   );
