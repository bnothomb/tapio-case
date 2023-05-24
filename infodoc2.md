# Case V2 : Decisions log and remarks

This document contains all the choices that have been made in the implementation of the second version and the response to the remarks received.


## Updates 
Non-exhaustive, most important points only:
* Refactoring following the comments received
* Adding constraints to the models
* Adding support for ordered ReductionModification to a source
* Adding date field for a ReductionModification
* Change the ratio field to a sum field for modification


## Business decisions

The decisions are explained in the answers to the remarks




## Responses to the remarks

### Regarding Python
```
!= None, is None, len(source_list) == 0 etc..
```
I have two interpretations for this remark:
* Using 'if self.acquisition_year:' instead of 'if self.acquisition_year is not None:' 
	* I prefer the more explicit (though less elegant) version due to 0=False but if the convention at Tapio is to use the more concise one, I will adapt my coding style according to the company standard of course (I have adapted the code with the more concise version)
* Too few model validations -> new constraints on data models:
	* Define mandatory fields where it makes sense 
	* if lifetime is not empty then acquisition_year cannot be empty


```
functions:  year_delta_emission() and year_emission() are really alike, isn't it possible to remove duplicated code?
```
I didn't see a straigth forward solution, I will be happy to receive any suggestions.

### Models architecture / features:
```
How do you order the modifications among them?
```
For the first version, I decided to have the simplest possible modification system: only one modification per source, very limited modification possibility: change EF and a multiplier for the value. The choice of this simplicity was due to the complexity of clarifying the need precisely (easier in a meeting but not the purpose of the exercise) I did not want to waste time developing something with unnecessary complexity.

For this version, an order system was added with constraints to make it easier to implement (again, same idea, don't make a system unnecessarily complex):
* Added an 'order' field in ReductionModification(models.Model). For each source and each strategy, the order field is automatically incremented when a modification is added
* It is only possible to add a modification at the end of the modification list 
* Modifications must be in chronological order, i.e. it is not possible to add a modification with a lower date than the previous one
* It is possible to delete any modification (there is no need to have a continuous 'order', just sorted 'order')
* Rules to calculate the delta :
	* the value changes are added together if it is during the lifetime of the change 
	* the emission factor = the last emission factor set
	* Positive value when modifications reduce emissions
	* Cannot have a positive value if the initial source is already amortized (it makes no sense to "improve" something that is already zero)

	
```
How do you compute the emissions of a modified source in 2030 if acquired in 2026 with a lifetime of 5 ? (If the base source is in 2020)
```
It was decided to change the ratio to a sum operation (easier to do with lifetime).

Exemple : Modification = +1 to the source value.
Source emission factor = 10

Delta = total emission without modification - emission with modification

Delta = 0 (allready amortized) - 1*10/5 = -2

The value is negative, which represents an increase in emission (which is logical since we have incremented the value).


```
For the logical split of functionalities, I'ld prefer if source was not modified with a strategy field, how else could you store that info? What impact would that have on the endpoints?
```
The strategy field in the source represents the case where we wish to add a new source to a strategy. This source is linked to the strategy and not to the report (important distinction for the calculation of emissions).

Another possibility to store the value is to adapt the modification to also represent the addition of a new source. This solution has the disadvantage of leaving the reporting field of the corresponding source empty.

As the model is decoupled from the endpoints (the views), there is no impact if desired. (This avoids breaking changes for the clients).


### Optimisation
```
2 loops included in the sum() functions?
```
I don't think I know what loop you are talking about unfortunately. The 2 sum() in ReductionStrategy.year_delta_emission ? If yes, they are:
* One for the sum of the modifications
* One for the sum of the new sources related to the strategy (these emissions must be subtracted from the emissions gained)

```
The points about the order of the modifications will be particularly interesting regarding the optimization
```
Done, see explaination above.

### Django
```
You often use .order_by(), how could it be by default?
```
The default order is "ordered by id" (primary key). With pagination, however, an "UnorderedObjectListWarning" occurs and it is recommended to explicitly specify the desired order to avoid inconsistent results.

I think a better solution is to specify it explicitly through the Meta class in the ordering attribute in the Meta options of the template. This is what has been done.


```
Why Viewset instead of APIView ?
```
I chose ModelViewSet to simplify the code and reduce duplication as it is a straightforward CRUD API.
It is possible to switch to APIView if fine control and customisation of each API method is needed (which can be done on a view by view basis).


```
I liked the permissions touch, how would you include one to make sure that the user only access models they should have access to? (for example only specific reports and cie..)
```
'django.contrib.auth' provides a set of built-in permissions.
I can create a custom permission class that checks if the user has the 'coreapp.view_source' permission to view a source for example.