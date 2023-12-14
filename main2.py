import pygame
import sys
import numpy as np


class Zone:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 0, 0)  # Noir pour l'intérieur
        self.border_color = (255, 255, 255)  # Blanc pour le contour
        self.active_color = (173, 216, 230)  # Bleu clair pour la zone active

    def draw(self, surface, is_active=False):
        pygame.draw.rect(surface, self.active_color if is_active else self.color, self.rect)
    



class PongGame:
    def __init__(self, largeur_fenetre, hauteur_fenetre, vitesse_raquette, vitesse_balle):
        pygame.init()

        self.largeur_fenetre = largeur_fenetre
        self.hauteur_fenetre = hauteur_fenetre
        self.vitesse_raquette = vitesse_raquette
        self.vitesse_balle = vitesse_balle

        self.blanc = (255, 255, 255)
        self.noir = (0, 0, 0)

        self.fenetre = pygame.display.set_mode((largeur_fenetre, hauteur_fenetre))
        pygame.display.set_caption("Pong")

        self.raquette_droite = pygame.Rect(largeur_fenetre - 70, hauteur_fenetre // 2 - 50, 20, 100)
        self.balle = pygame.Rect(largeur_fenetre // 2 - 15, hauteur_fenetre // 2 - 15, 30, 30)

        #self.balle.x = np.random.randint(self.largeur_fenetre // 2 - 200, self.largeur_fenetre // 2 - 100)
        #self.balle.y = np.random.randint(0, self.hauteur_fenetre - 30)

        self.balle.x = (self.largeur_fenetre // 2 - 200)
        self.balle.y = (self.hauteur_fenetre // 2 - 200)

        direction_x = 1#np.random.choice([-1, 1])
        direction_y = 1#np.random.choice([-1, 1])

        #direction_x = 1
        #direction_y = 0

        self.direction_balle_x = direction_x
        self.direction_balle_y = direction_y

        #game_over = False
        self.score = 0
        self.reward = 0
        self.police = pygame.font.Font(None, 36)

        self.en_collision_raquette = False  # Nouvelle variable pour gérer la collision avec la raquette

        nb_lignes = 20
        nb_colonnes = 20
        zone_width = largeur_fenetre // nb_colonnes
        zone_height = hauteur_fenetre // nb_lignes

        self.zones = [Zone(x * zone_width, y * zone_height, zone_width, zone_height) for y in range(nb_lignes) for x in range(nb_colonnes)]

    
    def reinitialiser_partie(self):
        self.raquette_droite.y = self.hauteur_fenetre // 2 - 50
        #self.balle.x = np.random.randint(self.largeur_fenetre // 2 - 200, self.largeur_fenetre // 2 - 100)
        #self.balle.y = np.random.randint(0, self.hauteur_fenetre - 30)
        #self.balle.x = self.largeur_fenetre // 2 - 150
        #self.balle.y = self.hauteur_fenetre - 15
        self.balle.x = (self.largeur_fenetre // 2 - 200)
        self.balle.y = (self.hauteur_fenetre // 2 - 200)
        direction_x = 1#np.random.choice([-1, 1])
        direction_y = 1#np.random.choice([-1, 1])

        #direction_x = 1
        #direction_y = 0



        self.direction_balle_x = direction_x
        self.direction_balle_y = direction_y
        self.score = 0
        self.reward = 0



    def deplacer_raquette(self):
        touches = pygame.key.get_pressed()
        if touches[pygame.K_UP] and self.raquette_droite.top > 0:
            self.raquette_droite.y -= self.vitesse_raquette
        if touches[pygame.K_UP] and self.raquette_droite.top == 0:
            #self.reward -= 1
            pass
        if touches[pygame.K_DOWN] and self.raquette_droite.bottom < self.hauteur_fenetre:
            self.raquette_droite.y += self.vitesse_raquette
        if touches[pygame.K_DOWN] and self.raquette_droite.bottom == self.hauteur_fenetre:
            #self.reward -= 1
            pass
        

    def deplacer_raquette_agent(self, action):
        #print("raquette_droite.bottom : ",self.raquette_droite.bottom,"      balle.y", self.balle.y, "    raquette_droite.top : ", self.raquette_droite.top)
        if action[0]==1 and self.raquette_droite.top > 0:
            self.raquette_droite.y -= self.vitesse_raquette
            self.reward += 0.2
        ##if action[0]==1 and self.raquette_droite.top == 0:
            ##self.reward -= 10
            ##pass
        if action[1]==1 and self.raquette_droite.bottom < self.hauteur_fenetre:
            self.raquette_droite.y += self.vitesse_raquette
            self.reward += 0.2

        ##if action[1]==1 and self.raquette_droite.bottom == self.hauteur_fenetre:
            ##self.reward -= 10`
            ##pass
        if action[2]==1:
            self.raquette_droite.y += 0


        
        

    def deplacer_balle(self):
        self.balle.x += self.direction_balle_x * self.vitesse_balle
        self.balle.y += self.direction_balle_y * self.vitesse_balle
    """
    def rebondir_balle(self):
        if self.balle.top <= 0 or self.balle.bottom >= self.hauteur_fenetre:
            self.direction_balle_y *= -1
        if self.balle.left <= 0:
            self.direction_balle_x *= -1

        # Ajout de la vérification pour la collision avec la raquette
        if (self.balle.colliderect(self.raquette_droite) and not self.en_collision_raquette):
            self.direction_balle_x *= -1
            #self.score += 1
            #self.reward += 10
            self.en_collision_raquette = True
       
    """

    def rebondir_balle(self):
        if self.balle.top <= 0 or self.balle.bottom >= self.hauteur_fenetre:
            self.direction_balle_y *= -1
        if self.balle.left <= 0:
            self.direction_balle_x *= -1

        # Ajout de la vérification pour la collision avec la raquette
        if (self.balle.colliderect(self.raquette_droite) and not self.en_collision_raquette):
            self.direction_balle_x *= -1
            self.en_collision_raquette = True
            self.score += 1
            #self.reward = 1000*(self.score**2)
            self.reward += 10


        # Si la balle n'est plus en collision avec la raquette, réinitialiser la variable
        if not self.balle.colliderect(self.raquette_droite):
            self.en_collision_raquette = False

    def gestion_collision_murs(self):
        if self.balle.right >= self.largeur_fenetre:
            # Réinitialisation du score uniquement lorsque la balle touche le mur de droite
            #self.reward -= 1000
            self.reward -= 10

            #self.reinitialiser_partie()

            return True
        #game_over = False
        self.reward += 0.01
        return False
    
    def collision(self,pt):
        collision = False
        if (self.balle.colliderect(pt) and not pt):
            collision = True
            
        return collision

    
    def balle_raquette(self):
        if self.direction_balle_x == 1 and self.balle.x>self.largeur_fenetre/2  and abs(self.balle.y - (self.raquette_droite.top - self.raquette_droite.bottom)) < self.hauteur_fenetre/5:
            self.reward += 0.01
        if self.direction_balle_x == 1 and self.balle.x>self.largeur_fenetre/2 and abs(self.balle.y - (self.raquette_droite.top - self.raquette_droite.bottom)) > self.hauteur_fenetre/5:
            self.reward -= 0.01



        # Si la balle n'est plus en collision avec la raquette, réinitialiser la variable
        if not self.balle.colliderect(self.raquette_droite):
            self.en_collision_raquette = False
    
    def geo(self):
        #return np.array([self.raquette_droite.y, self.balle.x, self.balle.y, self.direction_balle_x, self.direction_balle_y, self.vitesse_balle, self.score], dtype=int)
        return np.array([self.raquette_droite.y, self.balle.y, self.direction_balle_y], dtype=int)
    """
    def gestion_collision_murs(self):
        game_over = False
        if self.balle.left <= 0:
            self.direction_balle_x *= -1

        if self.balle.right >= self.largeur_fenetre:
            # Réinitialisation du score uniquement lorsque la balle touche le mur de droite
            self.reward = -10
            self.balle.x = self.largeur_fenetre // 2 - 15
            self.balle.y = self.hauteur_fenetre // 2 - 15
            self.direction_balle_x *= -1

            if not game_over:
                self.score = 0  # Réinitialisation du score uniquement si l'épisode n'est pas déjà terminé

            game_over = True
            return game_over

        return game_over
    
    """

    def dessiner_elements(self):
        self.fenetre.fill(self.noir)

        # Dessiner les zones
        #for i, zone in enumerate(self.zones):
            #zone.draw(self.fenetre, is_active=zone.rect.collidepoint(self.balle.x, self.balle.y))
            #print(i, zone.rect, zone.rect.collidepoint(self.balle.x, self.balle.y))
        # Dessiner la raquette et la balle
        pygame.draw.rect(self.fenetre, self.blanc, self.raquette_droite)
        pygame.draw.rect(self.fenetre, self.blanc, self.balle)

        # Afficher le score et la récompense
        texte_score = self.police.render("Score: {}".format(self.score), True, self.blanc)
        self.fenetre.blit(texte_score, (10, 10))

        texte_reward = self.police.render("Reward: {}".format(self.reward), True, self.blanc)
        self.fenetre.blit(texte_reward, (10, 30))

        pygame.display.flip()


    def step(self, action):
        # Effectuer l'action donnée par l'agent
        self.deplacer_raquette_agent(action)  # Vous pouvez ajuster cette méthode en fonction de l'action
        self.deplacer_balle()
        #self.balle_raquette()
        self.rebondir_balle()
        #print("test condition", self.raquette_droite.bottom, self.balle.y, self.raquette_droite.top)
        #if self.raquette_droite.bottom>self.balle.y>self.raquette_droite.top:
            #print("xs,nsnx,qxs,nqxsn,qxsn,qxn,qxsn,")
            #self.reward += 100
        done = self.gestion_collision_murs()
        self.dessiner_elements()

        #print(self.zones[0])

        # Obtenez le nouvel état après l'action
        #new_state = self.geo()

        # Calculez la récompense en fonction de l'état actuel (avant l'action) et du nouvel état
        #reward = self.score  # Vous pouvez ajuster la logique de récompense en fonction de vos besoins

        # Vérifiez si l'épisode est terminé
        # Vous devrez implémenter la logique pour déterminer si l'épisode est terminé
        #print(done)

        pygame.time.Clock().tick(1000)
        return self.score, self.reward, done

    def executer(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            

            self.deplacer_raquette()
            self.deplacer_balle()
            self.balle_raquette()
            self.rebondir_balle()
            done = self.gestion_collision_murs()
            self.dessiner_elements()
            if done:
                self.reinitialiser_partie()
            #print(self.geo(), self.reward, self.gestion_collision_murs())


            pygame.time.Clock().tick(60)

if __name__ == "__main__":
    pong = PongGame(800, 600, 30, 15)
    pong.executer()
    #while True:
