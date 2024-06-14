'use client'

import { useBorrowingStore } from '@/store/borrowing-store'
import { IVideoBorrowing } from '@/types'
import { BorrowingItem } from './borrowing-item'

export const BorrowingTable = () => {
  const { videoBorrowings } = useBorrowingStore()

  if (!videoBorrowings.length) {
    return null
  }

  return (
    <div className='flex h-full items-center w-full justify-start'>
      <div className='relative w-full h-full flex flex-col items-center justify-center'>
        <div className='flex flex-col w-full h-full'>
          <div className='overflow-x-auto'>
            <div className='align-middle inline-block min-w-full sm:px-6 lg:px-'>
              <div className='shadow overflow-hidden sm:rounded-lg'>
                <table className='min-w-full divide-y dark:divide-slate-600'>
                  <thead className='bg-slate-800'>
                    <tr>
                      <th
                        scope='col'
                        className='px-6 py-3 text-left text-xs font-medium dark:text-slate-400  uppercase tracking-wider'
                      >
                        Название
                      </th>
                      <th
                        scope='col'
                        className='px-6 py-3 text-left text-xs font-medium dark:text-slate-400  uppercase tracking-wider'
                      >
                        ID
                      </th>
                      <th
                        scope='col'
                        className='px-6 py-3 text-left text-xs font-medium dark:text-slate-400  uppercase tracking-wider'
                      >
                        Оригинал
                      </th>
                      <th
                        scope='col'
                        className='px-6 py-3 text-left text-xs font-medium dark:text-slate-400  uppercase tracking-wider'
                      >
                        Начало
                      </th>
                      <th
                        scope='col'
                        className='px-6 py-3 text-left text-xs font-medium dark:text-slate-400  uppercase tracking-wider'
                      >
                        Конец
                      </th>
                    </tr>
                  </thead>
                  <tbody className='relative divide-y dark:divide-slate-600'>
                    {videoBorrowings.map(
                      (item: IVideoBorrowing, index: number) => {
                        return (
                          <BorrowingItem
                            key={`${item.id}${index}`}
                            end={item.end}
                            id={item.id}
                            nameVideo={item.nameVideo}
                            originalLink={item.originalLink}
                            start={item.start}
                          />
                        )
                      }
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
