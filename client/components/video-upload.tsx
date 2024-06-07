import Image from 'next/image'
import { forwardRef } from 'react'

import CircleXIcon from '@/assets/circle-x.svg'
import { cn } from '@/lib/utils'
import PreviewImage from '@/assets/wallpaper.jpg'
import { VideoSize } from './video-size'
import { ProgressBar } from './progress-bar'

interface ImageUploadProps extends React.HTMLAttributes<HTMLTableRowElement> {
  name: string
  size: number
  type: string
  error?: boolean | undefined
  progress: number
}

export const VideoUpload = forwardRef<HTMLTableRowElement, ImageUploadProps>(
  ({ error, name, size, className, progress, ...props }, ref) => {
    return (
      <tr
        ref={ref}
        {...props}
        className={cn('', className)}
      >
        <td className='px-6 py-4 whitespace-nowrap text-sm dark:text-slate-400'>
          <div className='relative flex h-12 w-20'>
            {error ? (
              <div className='flex w-full justify-center items-center'>
                <CircleXIcon className='h-6 w-6 dark:text-red-500' />
              </div>
            ) : (
              <Image
                style={{ objectFit: 'contain', borderRadius: '5px' }}
                src={PreviewImage}
                fill
                alt={name}
              />
            )}
          </div>
        </td>
        <td className='px-6 py-4 truncate whitespace-normal text-sm font-medium dark:text-slate-400 '>
          <div>
            <p
              className={cn('dark:text-slate-500', {
                'dark:text-red-500': error
              })}
            >
              {name}
            </p>
          </div>
        </td>
        <td
          className={cn(
            'px-6 py-4 whitespace-nowrap text-sm dark:text-slate-500',
            {
              'dark:text-red-500': error
            }
          )}
        >
          <VideoSize size={size} />
        </td>
        <td className='px-6 py-4 whitespace-nowrap text-sm dark:text-slate-400 '>
          <ProgressBar progress={progress} />
        </td>
      </tr>
    )
  }
)

VideoUpload.displayName = 'VideoUpload'
