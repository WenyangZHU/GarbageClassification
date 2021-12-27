#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pygame
import random
import sys

TTF_FILE = 'resources/ttf/FangZhengKaiTiJianTi.ttf'

WINDOW_SIZE = (1400, 700)
PAVEMENT_SIZE = (1400, 100)
GARBAGE_REC_SIZE = (120, 120)
GARBAGE_BORDER_WIDTH = 5
GARBAGE_BIN_REC_SIZE = (250, 250)

# Used color and font size definitions.
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREY = (169, 169, 169)
SCORE_ROUND_FONT_SIZE = 44
GARBAGE_NAME_FONT_SIZE = 36
FINISH_TEXT_FONT_SIZE = 60

PAVEMENT_POS = [0, 600]  # x, y
GARBAGE_POS = [150, 100, 125]  # x, y, interval x
GARBAGE_BIN_POS = [125, 430, 50]  # x, y, interval x
SCORE_POS = [10, 5]  # x, y
ROUND_POS = [1250, 5]  # x, y
FINISH_TEXT_POS = [400, 200]  # x, y
FINISH_SCORE_POS = [650, 300]  # x, y

# Number of objects.
GARBAGE_NUM = 5
TOTAL_ROUND = 10

class Garbage:
  def __init__(self, image, category, garbage_id, name, font):
    self.image = pygame.transform.scale(image, GARBAGE_REC_SIZE)
    self.category = category
    self.id = garbage_id
    self.name = name
    self.font = font
    self.pos = (0, 0)
    self.rect = image.get_rect()
    self.rect.w, self.rect.h = GARBAGE_REC_SIZE[0], GARBAGE_REC_SIZE[1]
    self.image_border = pygame.draw.rect(self.image, RED, self.rect, GARBAGE_BORDER_WIDTH)
    self.text = self.font.render(name, False, BLACK)
    self.text_rect = self.text.get_rect()

  def set_pos(self, pos):
    self.pos = pos
    self.rect.x, self.rect.y = 0, 0
    self.rect.move_ip(pos)
    self.text_rect.center = (pos[0] + self.rect.w / 2, pos[1] + self.rect.h + 30)

  def move(self, rel):
    self.rect.move_ip(rel)

  def reset(self):
    self.rect.x, self.rect.y = self.pos

  def remove(self):
    self.image.set_alpha(0)
    self.rect.w, self.rect.h = 0, 0
    self.text_rect.w, self.text_rect.h = 0, 0


class GarbageBin:
  def __init__(self, image, category):
    self.image = pygame.transform.scale(image, GARBAGE_BIN_REC_SIZE)
    self.category = category
    self.pos = (0, 0)
    self.rect = image.get_rect()
    self.rect.w, self.rect.h = GARBAGE_BIN_REC_SIZE[0], GARBAGE_BIN_REC_SIZE[1]

  def set_pos(self, pos):
    self.pos = pos
    self.rect.x, self.rect.y = 0, 0
    self.rect.move_ip(pos)


class Text:
  def __init__(self, font):
    self.font = font
    self.pos = (0, 0)
    self._update()
    self.text_rect = self.text.get_rect()

  def set_pos(self, pos):
    self.pos = pos
    self.text_rect.x, self.text_rect.y = 0, 0
    self.text_rect.move_ip(pos)

  def _update(self):
    pass


class Score(Text):
  def __init__(self, font):
    self.score = 0
    super().__init__(font)

  def add(self):
    self.score += 1
    self._update()

  def minus(self):
    self.score -= 1
    self._update()

  def _update(self):
    self.text = self.font.render('分数: {:d}'.format(self.score), False, BLUE)


class Round(Text):
  def __init__(self, font):
    self.round = 0
    super().__init__(font)

  def next(self):
    self.round += 1
    self._update()

  def _update(self):
    self.text = self.font.render('关卡: {:d}'.format(self.round), False, RED)


class FinishText(Text):
  def __init__(self, font):
    super().__init__(font)

  def _update(self):
    self.text = self.font.render('恭喜顺利完成垃圾分类！', False, BLACK)


def get_selected_garbage(garbages, round_num):
  current_x, current_y, interval_x = GARBAGE_POS
  selected_garbages = set()
  for garbage in garbages[round_num * GARBAGE_NUM:(round_num + 1) * GARBAGE_NUM]:
    selected_garbages.add(garbage)
  for garbage in selected_garbages:
    garbage.set_pos((current_x, current_y))
    current_x += interval_x + GARBAGE_REC_SIZE[0]
  return selected_garbages


def main():
  pygame.init()
  pygame.display.set_caption('Garbage Classification')
  icon = pygame.image.load('resources/images/icon.png')
  pygame.display.set_icon(icon)

  screen = pygame.display.set_mode(WINDOW_SIZE)
  BACKGROUND = (255, 165, 0)
  score_round_font = pygame.font.Font(TTF_FILE, SCORE_ROUND_FONT_SIZE)
  garbage_name_font = pygame.font.Font(TTF_FILE, GARBAGE_NAME_FONT_SIZE)
  finish_text_font = pygame.font.Font(TTF_FILE, FINISH_TEXT_FONT_SIZE)

  # Image Initialization
  image_dir = 'resources/images'
  garbage_bin_dir = os.path.join(image_dir, 'garbage_bins')
  category = 0
  garbage_id = 0
  garbages = []
  garbage_bins = []

  # Files are stored as:
  # - recyclable_waste.png indicates the garbage bin for recyclable garbage.
  # - recyclable_waste/0.png is one recycable garbage image.
  for garbage_bin_image in os.listdir(garbage_bin_dir):
    garbage_dir = os.path.join(image_dir, garbage_bin_image.split('.')[0])
    for garbage_image in os.listdir(garbage_dir):
      garbage_image_path = os.path.join(garbage_dir, garbage_image)
      garbages.append(Garbage(pygame.image.load(garbage_image_path), category, garbage_id, garbage_image.split('.')[0], garbage_name_font))
      garbage_id += 1
    garbage_bin_path = os.path.join(garbage_bin_dir, garbage_bin_image)
    garbage_bins.append(GarbageBin(pygame.image.load(garbage_bin_path), category))
    category += 1
  random.shuffle(garbages)

  score = Score(score_round_font)
  round = Round(score_round_font)
  finish_text = FinishText(finish_text_font)

  # Screen Initialization
  pavement = pygame.Surface(PAVEMENT_SIZE)
  pavement.fill(GREY)
  pavement_rect = pygame.Rect(PAVEMENT_POS, PAVEMENT_SIZE)

  current_x, current_y, interval_x = GARBAGE_BIN_POS
  for garbage_bin in garbage_bins:
    garbage_bin.set_pos((current_x, current_y))
    current_x += interval_x + GARBAGE_BIN_REC_SIZE[0]

  score.set_pos(SCORE_POS)
  round.set_pos(ROUND_POS)

  # Main loop
  round_end = True
  finish = False
  selected_garbages = set()
  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()

    if finish:
      # Final Screen
      screen.fill(BACKGROUND)
      screen.blit(finish_text.text, finish_text.text_rect)
      screen.blit(score.text, score.text_rect)
      pygame.display.flip()

      continue
    elif round_end:
      current_garbage = None
      round.next()
      if round.round > TOTAL_ROUND:
        finish = True

        # Final Screen Initialization
        finish_text.set_pos(FINISH_TEXT_POS)
        score.set_pos(FINISH_SCORE_POS)

        continue
      round_end = False
      selected_garbages = get_selected_garbage(garbages, round.round)

    mouse_pos = pygame.mouse.get_pos()
    rel = pygame.mouse.get_rel()
    if pygame.mouse.get_pressed()[0]:
      if current_garbage:
        current_garbage.move(rel)
      else:
        for garbage in selected_garbages:
          if garbage.rect.collidepoint(mouse_pos):
            current_garbage = garbage
            break
    # Release the mouse.
    elif current_garbage:
      for garbage_bin in garbage_bins:
        if garbage_bin.rect.collidepoint(mouse_pos):
          if current_garbage.category == garbage_bin.category:
            score.add()
            current_garbage.remove()
            selected_garbages.remove(current_garbage)
            if not selected_garbages:
              round_end = True
          else:
            score.minus()
          break
      current_garbage.reset()
      current_garbage = None

    screen.fill(BACKGROUND)
    screen.blit(pavement, pavement_rect)
    screen.blit(score.text, score.text_rect)
    screen.blit(round.text, round.text_rect)
    for garbage_bin in garbage_bins:
      screen.blit(garbage_bin.image, garbage_bin.rect)
    for garbage in selected_garbages:
      screen.blit(garbage.text, garbage.text_rect)
      screen.blit(garbage.image, garbage.rect)
    pygame.display.flip()


if __name__ == '__main__':
  main()