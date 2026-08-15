import type { TagTreeVO } from '@/types'

export interface FlatTagNode {
  tag: TagTreeVO
  depth: number
}

/**
 * 将标签树按深度优先展平为带缩进深度的列表
 */
export function flattenTagTree(
  nodes: TagTreeVO[],
  depth = 0,
  acc: FlatTagNode[] = [],
): FlatTagNode[] {
  for (const n of nodes) {
    acc.push({ tag: n, depth })
    if (n.children && n.children.length) {
      flattenTagTree(n.children, depth + 1, acc)
    }
  }
  return acc
}
